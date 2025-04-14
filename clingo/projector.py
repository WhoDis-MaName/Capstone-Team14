#!/usr/bin/env python

from __future__ import print_function
import clingo, clingo.ast, sys, time, json, random, argparse
from random import Random

try:
    input = raw_input
except NameError:
    pass

output_list = ['ground', 'solve', 'rewrite']

# Setup variables
VERSION = '1.0.0'
class Setting:
    OUTPUT = 'solve'
    DEBUG = 0
    MAX_ATOM_PROJECTION_COUNT = float('inf')
    RESTRICT = 'alpha'
    NORMALIZE = True
    LIMIT = float('inf')
    DEBUG_AFTER = float('inf')
    RANDOM = 0
    ORACLE = False
    DESCENDING = False


answer_queue = []
oracle_done = False
random = Random()
random_rules = Random()

class ASTVisitor(object):

    def visit(self, x):
        if isinstance(x, clingo.ast.AST):
            attr = "visit_" + str(x.type)
            if hasattr(self, attr):
                return getattr(self, attr)(x)
            else:
                after = self.visit_children(x)
                return after
        elif isinstance(x, list):
            return [self.visit(y) for y in x]
        elif x is None:
            return x
        else:
            raise TypeError("unexpected type (%s)" % type(x))

    def visit_children(self, x):
        for key in x.child_keys:
            child_x = self.visit(getattr(x, key))
            x[key] = child_x
        return x

class VariableCounter:
    """This class is used to track how much a variable is used within a rule"""
    def __init__(self):
        self.body_size = -1
        self.clean()
    
    def clean(self):
        self.variable_literal_dict = {} # Maps a variable to a set of containing functions
        self.unsafe_vars = set()
        self.unsafe_literals = set()
        self.variable_counts = {}
        self.safety_links = {}
    
    def post_process(self):
        dprint('DICT BEFORE LINK: %s' % self.variable_literal_dict, 3)
        dprint('Safety Links: %s' % self.safety_links, 3)
        new_literal_dict = {}
        for var in self.variable_literal_dict.keys():
            if var not in self.safety_links:
                new_literal_dict[var] = self.variable_literal_dict[var]
            else:
                new_literal_dict[var] = self.merge_safety_set(var)
        self.variable_literal_dict = new_literal_dict

        dprint('DICT AFTER LINK:  %s' % self.variable_literal_dict, 3)
        for unsafe_var in self.unsafe_vars:
            self.clean_var(unsafe_var.ast)
        for unsafe_literal in self.unsafe_literals:
            self.clean_literal(unsafe_literal.ast)
        dprint('DICT AFTER CLEAN: %s' % self.variable_literal_dict, 3)
    
    def merge_safety_set(self, var, done=None):
        if done is None:
            done = set()
        merged_set = set()
        for link_var in self.safety_links[var]:
            if link_var not in self.variable_literal_dict:
                raise Exception('Tried to merge links but no var key is in the alpha dict')
            if link_var in done:
                add_set = self.variable_literal_dict[link_var] # Base
            else:
                done.add(link_var)
                add_set = self.merge_safety_set(link_var, done)
            merged_set = merged_set.union(add_set)
        return merged_set

    def mark_var_unsafe(self, var):
        """Marks the variable as being unsafe for use in projection, removes variable from dict if already exists
        A variable should be unsafe if it matches any of the following: TODO Some of these conditions might be able to be worked around
        1.) The variable is in the head of the rule
        2.) The variable is used in an aggregate
        3.) The variable is used in an atom that is within another atom's arguments i.e. a(b(X))
        4.) The variable is used in all atoms of the body (therefore projection would not be of use)
        5.) The variable is used in greater than or equal to MAX_ATOM_PROJECITON_COUNT atoms in the body
        """
        dprint('Found unsafe var: %s' % var, 3)
        self.unsafe_vars.add(ASTWrapper(var))

    def mark_literal_unsafe(self, literal):
        dprint('Unsafe literal: %s' % literal, 3)
        self.unsafe_literals.add(ASTWrapper(literal))

    def clean_var(self, var):
        wrapped_var = ASTWrapper(var)
        if wrapped_var in self.variable_literal_dict:
            del self.variable_literal_dict[wrapped_var]
    
    def clean_literal(self, literal):
        wrapped_literal = ASTWrapper(literal)
        for wrapped_var, wrapped_literal_set in dict(self.variable_literal_dict).items():
            size_before = len(wrapped_literal_set)
            wrapped_literal_set = set([o_wrapped_literal for o_wrapped_literal in wrapped_literal_set if o_wrapped_literal != wrapped_literal])
            size_after = len(wrapped_literal_set)
            if size_after < size_before:
                # Function was removed, this variable is also unsafe
                dprint('Marking %s unsafe due to literal (%s) being unsafe' % (wrapped_var.ast, literal), 3)
                self.mark_var_unsafe(wrapped_var.ast)
                if len(wrapped_literal_set) > 0:
                    self.variable_literal_dict[wrapped_var] = wrapped_literal_set
    
    def is_var_unsafe(self, var):
        """Returns whether or not var is unsafe"""
        return ASTWrapper(var) in self.unsafe_vars

    def is_literal_unsafe(self, literal):
        """Returns whether or not literal is unsafe"""
        return ASTWrapper(literal) in self.unsafe_literals
    
    def add_literal_to_variable(self, var, literal):
        """Adds a function to the set of containing functions for a variable
        If it detects that this variable is used across the entire body
        (by comparing the # of functions in the partition to the body size)
        or that the variable is shared across MAX_ATOM_PROJECTION_COUNT literals,
        it will mark the variable as unsafe instead
        """
        wrapped_var = ASTWrapper(var)
        if wrapped_var not in self.variable_literal_dict:
            self.variable_literal_dict[wrapped_var] = set()
        if len(self.variable_literal_dict[wrapped_var]) >= Setting.MAX_ATOM_PROJECTION_COUNT:
            dprint('Marking %s unsafe due to exceeding MAX_ATOM_PROJECTION_COUNT' % var, 3)
            self.mark_var_unsafe(var)
        
        self.variable_literal_dict[wrapped_var].add(ASTWrapper(literal))
        return True

    def create_link(self, var_set):
        dprint('Link created for vars: %s' % var_set, 3)
        for var in var_set:
            if var in self.safety_links:
                self.safety_links[var] = self.safety_links[var].union(var_set) # Var already has links, union all links
            else:
                self.safety_links[var] = var_set # First link for var

    def get_largest_partition(self):
        """Returns the largest partition. If two partitions have the same size the first one encountered will be used."""
        largest_size = -1
        largest_partition = (None, None)
        for wrapped_var, wrapped_literal_set in self.variable_literal_dict.items():
            check_size = len(wrapped_literal_set)
            if check_size > largest_size:
                largest_size = check_size
                largest_partition = (wrapped_var, wrapped_literal_set)
        return largest_partition

class Transformer:
    """This class is the basis of rewrites on the logic program
    
    The class stores a reference of every rule in the program (for debugging purposes).
    It also redirects rules to the ProjectionTransformer for rewriting.
    """
    def __init__(self, builder):
        self.builder = builder
        self.built = False
        self.stms = []
        self.projection_cache = {}
        self.used_predicate_symbols = set()
        self.total_projection_count = 0
        self.projection_counts = {}
        self.pending_projection_counts = {}
        self.projected_rule_id_count = 0
        self.body_functions = {}
        self.head_functions = {}
        self.no_rewrite = False
        if Setting.ORACLE:
            self.answer_queue = answer_queue[:] # Clone list
            self.queue_done = False
            self.tried_y = False

    def visit(self, x):
        if isinstance(x, clingo.ast.AST):
            if x.type == clingo.ast.ASTType.Rule:
                return self.handle_rule(x)
            else:
                return x
        elif x is None:
            return x
        else:
            raise TypeError("unexpected type")

    def handle_rule(self, rule):
        if self.no_rewrite:
            return rule
        if Setting.RESTRICT == 'alpha':
            tau = alpha
        elif Setting.RESTRICT == 'beta':
            tau = beta
        else:
            raise Exception('Restriction "%s" is not supported' % Setting.RESTRICT)
        rule, projected_rules = self.projection(rule, tau)
        for projected_rule in projected_rules:
            self.add_stm(projected_rule)
        return rule

    def prepare_stm(self, stm):
        if Setting.NO_REWRITE:
            parsed_stm = stm
            if Setting.ORACLE:
                global oracle_done
                oracle_done = True
        else:
            parsed_stm = self.visit(stm)
        return self.add_stm(parsed_stm)
    
    def add_stm(self, stm):
        self.stms.append(stm)
    
    def build_program(self):
        if self.built:
            raise Exception('Program has already been built for this transformer')
        # self.make_projected_functions_uniq() FIXME Not perfect with linking, need to look into
        for stm in self.stms:
            self.builder.add(stm)
        self.built = True
    
    def equal_projection_rules(self, ruleA, ruleB):
        """Used to check equality between projection so the same projection is not performed twice"""
        if not isinstance(ruleA, clingo.ast.AST) or not isinstance(ruleB, clingo.ast.AST):
            return False
        if not ruleA.type == clingo.ast.ASTType.Rule or not ruleB.type == clingo.ast.ASTType.Rule:
            return False
        # Both are at least rules
        if not hasattr(ruleA, "proj_metadata") or not hasattr(ruleB, "proj_metadata"):
            return False
    
    def make_projected_functions_uniq(self):
        """Makes all functions located in self.projected_functions have unique names within the program"""
        dprint('~~~MAKING PROJECTED FUNCTIONS UNIQUE~~~', 3)
        for projected_rule_id, head_fun in self.head_functions.items():
            dprint('Checking [%s]: %s' % (projected_rule_id, head_fun), 3)
            if projected_rule_id not in self.body_functions or len(self.body_functions[projected_rule_id]) == 0:
                continue
            fun_name = self.body_functions[projected_rule_id][0].name # We just need to grab any of the names, the first one works
            while fun_name in self.used_predicate_symbols: # Find unique name
                fun_name += "'"
            self.used_predicate_symbols.add(fun_name)
            if fun_name != self.body_functions[projected_rule_id][0].name:
                dprint('New name: %s' % fun_name, 3)
                dprint('Updating body functions: %s' % self.body_functions[projected_rule_id], 4)
            for body_fun in self.body_functions[projected_rule_id]: # Rename all body functions to the unique name
                body_fun.name = fun_name
            head_fun.name = fun_name # Rename head function in the projected rule to the unique name
        dprint('', 3)
    
    def add_to_cache(self, rule):
        """Adds the rule to the cache
        Returns True if the rule was added to the cache, False otherwise
        """
        wrapped_rule = ASTWrapper(rule)
        if wrapped_rule in self.projection_cache:
            # Already did this projection somewhere
            projected_rule_id = self.projection_cache[wrapped_rule]
            # dprint('Reusing rule: %s [%d]' % (rule, projected_rule_id))
            return (False, projected_rule_id)
        else:
            # New projection
            projected_rule_id = self.projected_rule_id_count
            self.projected_rule_id_count += 1
            self.projection_cache[wrapped_rule] = projected_rule_id
            # dprint('New rule: %s [%d]' % (rule, projected_rule_id))
            return (True, projected_rule_id)

    def add_head_and_body_function_link(self, projected_rule_id, head_fun, body_fun):
        """Adds a function to be associated with the projected rule id to ensure any function renaming will apply"""
        if projected_rule_id not in self.head_functions:
            self.head_functions[projected_rule_id] = head_fun
        self.add_body_function_link(projected_rule_id, body_fun)
        setattr(head_fun, 'projected_rule_id', projected_rule_id)

    def add_body_function_link(self, projected_rule_id, body_fun):
        if projected_rule_id not in self.body_functions:
            self.body_functions[projected_rule_id] = []
        self.body_functions[projected_rule_id].append(body_fun)
        setattr(body_fun, 'projected_rule_id', projected_rule_id)

    def projection(self, rule, tau):
        alpha_dict = AlphaDictionaryBuilder(self).get_alpha_dict(rule)
        tau_rules = []
        while len(alpha_dict) > 0:
            if self.total_projection_count == Setting.DEBUG_AFTER:
                Setting.DEBUG = 1
            if Setting.LIMIT <= self.total_projection_count:
                return rule, []
            dprint('Alpha-Dict: %s' % alpha_dict, 2)
            if not Setting.DESCENDING:
                (selected_var, selected_literal_set) = self.get_smallest_alpha_pair(alpha_dict)
            else:
                (selected_var, selected_literal_set) = self.get_largest_alpha_pair(alpha_dict)
            dprint('Selected: (%s, %s)' % (selected_var, selected_literal_set), 2)
            
            projectable_vars = set([selected_var])
            for wrapped_var, wrapped_literal_set in alpha_dict.items():
                if wrapped_var == selected_var:
                    continue
                if alpha(self, rule, wrapped_var.ast).issubset(tau(self, rule, selected_var.ast)):
                    dprint('Including %s in the projection' % wrapped_var, 2)
                    projectable_vars.add(wrapped_var)
            
            base_proj_size = len(selected_literal_set) # NOTE: Does not include bounding literals!
            self.queue_projection_count(base_proj_size)
            dprint('Projecting %s' % rule, 2)
            rule_before = str(rule)
            replacement_rule, tau_rule, prenamed_tau_rule = self.project(copy(rule, self), projectable_vars, tau)
            if tau_rule is not None and find_variables(tau_rule.body) == find_variables(rule.body):
                dprint('Skipping projection: tau rule contains same variables as base rule', 2)
                self.clear_pending_counts()
                self.projection_cache.pop(ASTWrapper(prenamed_tau_rule), None)
                del alpha_dict[selected_var]
                continue
            
            for projectable_var in projectable_vars:
                del alpha_dict[projectable_var]
            
            if tau_rule is not None:
                dprint('\nAdding rule: \033[93m%s\033[0m' % tau_rule)
            else:
                dprint('')
            dprint('Before projection: \033[94m%s\033[0m' % rule_before)
            dprint('After  projection: \033[92m%s\033[0m\n' % replacement_rule)
            if Setting.RANDOM_RULES:
                prompt_answer = random.choice(['y','n'])
                answer_queue.append(prompt_answer)
            elif Setting.ORACLE:
                global oracle_done
                if len(self.answer_queue) > 0:
                    prompt_answer = self.answer_queue.pop(0)
                    dprint('Answering with %s (%d)' % (prompt_answer, len(self.answer_queue)))
                    if len(self.answer_queue) <= 0:
                        oracle_done = True # Start by assuming we've done all projections
                else:
                    if not self.tried_y:
                        dprint('Trying "y"...')
                        prompt_answer = 'y'
                        self.tried_y = True
                    else:
                        dprint('Queue done...')
                        prompt_answer = 'n'
                        oracle_done = False # There are still more projections to do
            else:
                prompt_answer = dinput('Would you like to perform this projection? [y/n] ') # 'y' if not debug
                if Setting.DEBUG:
                    # Only store if in debug
                    answer_queue.append(prompt_answer)
            if prompt_answer == 'y*':
                dprint('Projecting this rule & stopping debug mode (future projections will occur)')
                Setting.DEBUG = 0
            elif prompt_answer == 'n':
                # NOTE WARNING: Selecting to skip will eliminate ALL candidate variables from consideration, possible need to rethink/revise to make skipping better
                dprint('Skipping...')
                self.clear_pending_counts()
                self.projection_cache.pop(ASTWrapper(prenamed_tau_rule), None)
                continue
            rule = replacement_rule
            if tau_rule is not None:
                tau_rules.append(tau_rule)
            
            self.commit_projection_counts()
        return rule, tau_rules
    
    def project(self, rule, projectable_vars, tau):
        replacement_rule = copy(rule, self)
        alpha_literals = alpha(self, replacement_rule, projectable_vars)
        if len(alpha_literals) == 0:
            raise Exception('Tried to project %s when no matching alpha literals were found' % projectable_vars)
        if tau == alpha:
            tau_literals = alpha_literals
        else:
            tau_literals = tau(self, replacement_rule, projectable_vars)
        loc = next(iter(alpha_literals)).ast.location # TODO Probably make this something like "N/A"
        tau_rule_body = [copy(literal_wrapper.ast) for literal_wrapper in tau_literals]
        alpha_vars = find_variables(alpha_literals)
        remaining_vars = alpha_vars - projectable_vars
        tau_function = clingo.ast.Function(loc, 'p_fun', [var_wrapper.ast for var_wrapper in remaining_vars], False)
        tau_rule = clingo.ast.Rule(loc,\
                        clingo.ast.Literal(loc, clingo.ast.Sign.NoSign, clingo.ast.SymbolicAtom(tau_function)),\
                        tau_rule_body)
        body_tau_function = copy(tau_function)

        # Normalize
        if Setting.NORMALIZE:
            tau_rule = RuleNormalizer().normalize(tau_rule) # TODO What if the literals are in different orders?
        prenamed_tau_rule = copy(tau_rule) # Copy so that renaming the head predicate doesn't apply to this rule
        is_rule_added, projected_rule_id = self.add_to_cache(prenamed_tau_rule)
        tau_function.name = 'p_fun_%d' % projected_rule_id
        body_tau_function.name = tau_function.name
        if is_rule_added:
            # It's a new rule
            dprint('New rule [%d]: %s' % (projected_rule_id, tau_rule), 3)
            dprint('(Projecting out %s)' % projectable_vars, 3)
        else:
            # Existing rule, don't add
            dprint('Existing rule [%d]: %s' % (projected_rule_id, tau_rule), 3)
            tau_rule = None

        replacement_rule.body = [body_atom for body_atom in replacement_rule.body if ASTWrapper(body_atom) not in alpha_literals]
        replacement_rule.body.append(clingo.ast.Literal(loc, clingo.ast.Sign.NoSign, clingo.ast.SymbolicAtom(body_tau_function)))
        return replacement_rule, tau_rule, prenamed_tau_rule

    def queue_projection_count(self, size):
        curr_count = self.pending_projection_counts.get(size, 0)
        self.pending_projection_counts[size] = curr_count + 1
    
    def commit_projection_counts(self):
        for size, p_count in self.pending_projection_counts.items():
            curr_count = self.projection_counts.get(size, 0)
            self.projection_counts[size] = curr_count + p_count
            self.total_projection_count += p_count
        self.clear_pending_counts()
    
    def clear_pending_counts(self):
        self.pending_projection_counts = {}

    def get_largest_alpha_pair(self, alpha_dict):
        """Returns the largest alpha-set"""
        smallest_size = -1
        smallest_pairs = []
        for var, literal_set in alpha_dict.items():
            check_size = len(literal_set)
            if check_size > smallest_size:
                smallest_size = check_size
                smallest_pairs = [(var, literal_set)]
            elif Setting.RANDOM and check_size == smallest_size:
                smallest_pairs.append((var, literal_set))
        return random.choice(smallest_pairs)
    
    def get_smallest_alpha_pair(self, alpha_dict):
        """Returns the smallest alpha-set"""
        smallest_size = float('inf')
        smallest_pairs = []
        for var, literal_set in alpha_dict.items():
            check_size = len(literal_set)
            if check_size < smallest_size:
                smallest_size = check_size
                smallest_pairs = [(var, literal_set)]
            elif Setting.RANDOM and check_size == smallest_size:
                smallest_pairs.append((var, literal_set))
        return random.choice(smallest_pairs)
        

class AlphaDictionaryBuilder(ASTVisitor):

    def __init__(self, base_transformer, variable_counter=None, tree_scope=None, parent_scope=None, ignore_head=False):
        self.base_transformer = base_transformer
        if variable_counter is None:
            self.variable_counter = VariableCounter()
        else:
            self.variable_counter = variable_counter
        if tree_scope is None:
            self.tree_scope = {}
        else:
            self.tree_scope = tree_scope
        self.tree_scope['parent_scope'] = parent_scope
        self.ignore_head = ignore_head
    
    def get_alpha_dict(self, rule):
        # self.tree_scope['rule'] = str(rule) # For debug usage
        self.visit(rule)
        if self.tree_scope.get('invalidate'):
            dprint('WARN: Skipping invalid rule: %s' % rule, 1)
            self.variable_counter.clean() # Something went wrong or we found a rule that can't be processed, skip!
        self.variable_counter.post_process()
        return self.variable_counter.variable_literal_dict

    def visit_children(self, x):
        for key in x.child_keys:
            if key == 'body':
                self.variable_counter.body_size = len(x[key])
            # Create a new/isolated scope so that children are not affected by siblings
            if isinstance(x[key], list):
                children = x[key]
                is_list = True
            else:
                children = [x[key]]
                is_list = False
            for index, child in enumerate(children): # Loop here to ensure a new scope is provided for immediate siblings
                child_tree_scope = dict(self.tree_scope)
                if key == 'head' or self.tree_scope.get('head'):
                    if self.ignore_head:
                        continue
                    child_tree_scope['head'] = True
                child_tree_scope['type'] = child.type if hasattr(child, 'type') else None
                child_tree_builder = AlphaDictionaryBuilder(self.base_transformer, self.variable_counter, child_tree_scope, self.tree_scope, self.ignore_head)
                children[index] = child_tree_builder.visit(child)
            if is_list:
                x[key] = children
            else:
                x[key] = children[0]
        return x

    def visit_Aggregate(self, aggregate):
        self.tree_scope['aggregate'] = True
        return self.visit_children(aggregate)

    def visit_BodyAggregate(self, body_aggregate):
        self.tree_scope['aggregate'] = True
        return self.visit_children(body_aggregate)

    def visit_Literal(self, literal):
        self.tree_scope['literal'] = literal
        return self.visit_children(literal)
    
    def visit_ConditionalLiteral(self, cond_literal):
        if not self.tree_scope.get('head') and 'literal' not in self.tree_scope:
            self.invalidate() # Can't process conditional literals at the body root safely without more consideration
        return self.visit_children(cond_literal)

    def visit_Function(self, fun):
        if self.tree_scope.get('function'):
            self.tree_scope['function_arg'] = True # This is a function within function
        else:
            self.tree_scope['function'] = fun
        self.base_transformer.used_predicate_symbols.add(fun.name)
        return self.visit_children(fun)

    def visit_Variable(self, var):
        dprint('Checking: %s' % var, 3)
        if self.tree_scope.get('head') or self.tree_scope.get('aggregate'):
            dprint('Marking %s unsafe due to variable being inside head/aggregate' % var, 3)
            self.variable_counter.mark_var_unsafe(var)
        else:
            dprint('Adding %s to partition for %s' % (self.tree_scope.get('literal'), var), 3)
            self.variable_counter.add_literal_to_variable(var, self.tree_scope.get('literal'))
            if not self.tree_scope.get('function') or self.tree_scope.get('literal') and self.tree_scope.get('literal').sign != clingo.ast.Sign.NoSign:
                sibling_vars = find_variables(self.tree_scope.get('literal'))
                self.variable_counter.create_link(sibling_vars)
        dprint('Checked: %s; Unsafe: %s' % (var, self.variable_counter.is_var_unsafe(var)), 3)
        return var
    
    def invalidate(self, scope=None):
        if scope is None:
            scope = self.tree_scope
        scope['invalidate'] = True
        parent_scope = scope.get('parent_scope')
        if parent_scope is not None:
            self.invalidate(parent_scope)

class VariableVisitor(ASTVisitor):

    def __init__(self):
        self.variable_counter = {}

    def visit_Variable(self, var):
        wrapped_var = ASTWrapper(var)
        var_count = self.variable_counter.get(wrapped_var, 0)
        self.variable_counter[wrapped_var] = var_count + 1
        return var

    def visit_Function(self, f):
        return self.visit_children(f)

    def variables(self):
        return set(self.variable_counter.keys())

    def count(self, var):
        return self.variable_counter.get(ASTWrapper(var), 0)

class ASTCopier(ASTVisitor):

    def __init__(self, transformer=None):
        self.base_transformer = transformer

    def deep_copy(self, ast):
        return self.visit(ast)

    def visit(self, x):
        if isinstance(x, clingo.ast.AST):
            dprint('Deep copying: %s [%s]' % (x, x.type), 4)
            x = clingo.ast.AST(x.type, **dict(x))
            if self.base_transformer and hasattr(x, 'projected_rule_id'):
                dprint('Copying head-body link in transformer [%d]: %s' % (x.projected_rule_id, x), 4)
                self.base_transformer.add_body_function_link(x.projected_rule_id, x)
            return super(ASTCopier, self).visit(x)
        else:
            return super(ASTCopier, self).visit(x)

class RuleNormalizer(ASTVisitor):
    """Renames all variables in a standardized way to help identify equivalent ASTs
    The first variable encountered (and all of its occurrences) will be renamed to V1, second variable to V2, etc.
    Additionally sorts the rule body
    """
    
    def normalize(self, ast):
        self.var_dict = {}
        return self.visit(ast)

    def visit_Variable(self, var):
        if var.name not in self.var_dict:
            normalized_name = 'V%d' % len(self.var_dict.keys())
            self.var_dict[var.name] = normalized_name
        else:
            normalized_name = self.var_dict[var.name]
        return clingo.ast.Variable(var.location, normalized_name)

    def visit_Rule(self, rule):
        if hasattr(rule, 'body'):
            rule.body.sort()
        return self.visit_children(rule)

class ASTWrapper(object):

    def __init__(self, ast):
        self.ast = ast
    
    def __hash__(self):
        return -hash(str(self.ast))

    def __str__(self):
        return '<%s>' % str(self.ast)
    
    def __repr__(self):
        return '<%s>' % repr(self.ast)
    
    def __eq__(self, other):
        return str(self.ast) == str(other.ast)
    
    def __ne__(self, other):
        return not self.__eq__(other)

# def new_control():
#     prg = clingo.Control()
#     prg.load('../parser-enc-inst-clingo-5/encodings/parser.prec.tucr1.clingo')
#     prg.use_enumeration_assumption = False
#     return prg

def read_encodings():
    full_prog = ''
    for encoding in Setting.ENCODINGS:
        full_prog += open(encoding).read()
    return full_prog

def print_settings():
    dprint('\n\t~[Settings]~')
    settings = [(attr, getattr(Setting,attr)) for attr in dir(Setting) if not attr.startswith("__")]
    for attr, value in settings:
        dprint('%s: %s' % (attr, value))
    dprint('')

def dprint(msg, level=1):
    if level <= Setting.DEBUG:
        print(msg)

def dinput(msg, level=1):
    if level <= Setting.DEBUG:
        return input(msg)
    return None

def pause(level=1):
    return dinput('Press ENTER to continue or type STOP to discontinue projecting further...\n', 1) == 'STOP'

def find_variables(ast):
    if type(ast) is set:
        ast = [a.ast for a in ast]
    var_visitor = VariableVisitor()
    var_visitor.visit(ast)
    return var_visitor.variables()

def copy(ast, transformer=None):
    """Deep copies an AST node. Will maintain head-body links if passed a Transformer."""
    dprint('Copying: %s' % ast, 4)
    copier = ASTCopier(transformer)
    copied = copier.deep_copy(ast)
    return copied

def alpha(transformer, rule, var):
    # TODO Replace alpha_dict usage with separate one that only builds for var
    alpha_dict = AlphaDictionaryBuilder(base_transformer=transformer, ignore_head=True).get_alpha_dict(rule)
    if type(var) in [list, set]:
        alpha_literals = set()
        for v in var:
            if type(v) is ASTWrapper:
                wrapped_var = v
            else:
                wrapped_var = ASTWrapper(v)
            alpha_literals = alpha_literals.union(alpha_dict.get(wrapped_var, set()))
    else:
        wrapped_var = ASTWrapper(var)
        alpha_literals = alpha_dict.get(wrapped_var, set())
    return alpha_literals

def beta(transformer, rule, var):
    alpha_literals = alpha(transformer, rule, var)
    alpha_vars = find_variables(alpha_literals)
    candidate_literals = alpha(transformer, rule, alpha_vars)
    beta_literals = alpha_literals
    for candidate in candidate_literals:
        if candidate in beta_literals:
            continue
        candidate_vars = find_variables(candidate.ast)
        if candidate_vars.issubset(alpha_vars):
            beta_literals.add(candidate)
    return beta_literals


class App:
    def __init__(self, args):
        # self.control = clingo.Control()
        self.args = args
    
    def apply_args(self):
        Setting.ENCODINGS = self.args.encoding
        Setting.OUTPUT = self.args.output
        Setting.DEBUG = args.debug
        Setting.MAX_ATOM_PROJECTION_COUNT = args.max_atoms if args.max_atoms > 0 else float('inf')
        Setting.RESTRICT = args.restrict
        Setting.NORMALIZE = args.no_normalize
        Setting.LIMIT = args.limit
        Setting.DEBUG_AFTER = args.debug_after
        Setting.RANDOM = args.random
        Setting.RANDOM_RULES = args.random_rules
        Setting.ORACLE = args.oracle
        Setting.NO_REWRITE = args.no_rewrite
        Setting.DESCENDING = args.descending
    
    def create_control(self):
        control = clingo.Control(['--warn=none'])
        control.use_enumeration_assumption = False
        if args.instance:
            for instance_path in args.instance:
                control.load(instance_path)
        return control

    def run(self):
        dprint('~~~~[DEBUG ENABLED]~~~~')
        print_settings()
        if Setting.RANDOM:
            random.seed(Setting.RANDOM)
        if Setting.RANDOM_RULES:
            random_rules.seed(Setting.RANDOM_RULES)
        smallest_grounded_rules = float('inf') # For oracle
        smallest_control = float('inf') # For oracle
        parse = True
        loop_count = 0
        while parse:
            loop_count += 1
            self.control = self.create_control()
            if not Setting.ORACLE:
                parse = False
            with self.control.builder() as b:
                t = Transformer(b)
                parse_start = time.time()
                clingo.parse_program(
                    read_encodings(),
                    lambda stm: t.prepare_stm(stm))
                t.build_program()
                parse_end = time.time()
                parse_time = parse_end - parse_start
            if Setting.ORACLE:
                ground_start = time.time()
                self.control.ground([('base', [])])
                ground_end = time.time()
                ground_time = ground_end - ground_start
                grounded_rules = self.control.statistics['problem']['lpStep']['rules']
                dprint('Grounding size WAS: %s' % smallest_grounded_rules)
                if loop_count == 1:
                    smallest_grounded_rules = grounded_rules
                    smallest_control = self.control
                    dprint('Base grounding size is %s' % smallest_grounded_rules)
                else:
                    dprint('Checking grounding size of %s' % grounded_rules)
                    if grounded_rules < smallest_grounded_rules:
                        smallest_grounded_rules = grounded_rules
                        smallest_control = self.control
                        answer_queue.append('y')
                        dprint('Changed grounding size to: %s' % smallest_grounded_rules)
                    else:
                        answer_queue.append('n')
                if oracle_done: # We've tried every first-selection projection
                    dprint('Oracle done.')
                    parse = False
                    self.control = smallest_control
                    break
                dprint('Answer queue: %s' % answer_queue)
        if Setting.OUTPUT == 'rewrite':
            for r in t.stms:
                print(r)
        else:
            if not Setting.ORACLE:
                ground_start = time.time()
                self.control.ground([('base', [])])
                ground_end = time.time()
                ground_time = ground_end - ground_start
                # print('BEFORE:')
                # print(json.dumps(self.control.statistics, sort_keys=True, indent=2, separators=(',', ': ')))
            if Setting.OUTPUT == 'solve':
                solve_start = time.time()
                ret = self.control.solve()
                solve_end = time.time()
                solve_time = solve_end - solve_start
                self.control.statistics['summary']['times']['py-solve'] = solve_time
                self.control.statistics['summary']['times']['py-gs'] = ground_time + solve_time
                self.control.statistics['summary']['times']['py-total'] = parse_time + ground_time + solve_time
                self.control.statistics['summary']['satisfiable'] = ret.satisfiable
            elif Setting.OUTPUT == 'ground':
                self.control.statistics['summary']['times']['py-total'] = parse_time + ground_time
            else:
                raise Exception('Unknown output setting')
            self.control.statistics['summary']['times']['py-parse'] = parse_time
            self.control.statistics['summary']['times']['py-ground'] = ground_time
            proj_stats = {
                'total': t.total_projection_count
            }
            for num, count in t.projection_counts.items():
                proj_stats[num] = count
            self.control.statistics['summary']['rewrites'] = {
                'projection': proj_stats
            }
            if len(answer_queue) > 0:
                self.control.statistics['summary']['choices'] = answer_queue
            print(json.dumps(self.control.statistics, sort_keys=True, indent=2, separators=(',', ': ')))

parser = argparse.ArgumentParser(description='Rewrites ASP logic program')
parser.add_argument('encoding', nargs='+', default=[], help='gringo source files')
parser.add_argument('--instance', action='append', help='adds an additional file to include in grounding/solving (will not be rewritten)')
parser.add_argument('--output', type=str, default='rewrite', help='the output mode of the program [%s]' % '|'.join(output_list))
parser.add_argument('--debug', type=int, default=0, help='enables pausing after projection & debug trace messages, value controls the level, 0 disables')
parser.add_argument('--max_atoms', type=int, default=-1, help='the maximum number of atoms a variable can be shared with in a rule while still performing projection, -1 for no max atoms')
parser.add_argument('--restrict', type=str, default='alpha', help='the restrict mode of the program')
parser.add_argument('--no_normalize', action='store_false', help='normalizes projected rules (NOTE: breaks caching for differently named variables)')
parser.add_argument('--limit', type=int, default=float('inf'), help='limits the number of projections performed, stopping projection after encountering the number specified')
parser.add_argument('--debug_after', type=int, default=float('inf'), help='enables debug mode after specified number of projections')
parser.add_argument('--random', type=int, default=0, help='provides a seed for randomness on equal heuristics, 0 to disable and always choose the first encountered (default)')
parser.add_argument('--random_rules', type=int, default=0, help='provides a seed for random choice selection on whether or not to perform a rewrite, 0 to disable (default)')
parser.add_argument('--oracle', action='store_true', help='predicts projections based on grounding size (will only improve solve time; grounding will occur many times)')
parser.add_argument('--no_rewrite', action='store_true', help='disables all rewriting and just parses the given program')
parser.add_argument('--descending', action='store_true', help='makes the alpha set selection choose LARGEST sets first')
parser.add_argument('--version', action='store_true', help='prints the version of Projector')

args = parser.parse_args()
if args.version:
    print('Projector version %s' % VERSION)
    sys.exit(0)
if args.output not in output_list:
    parser.print_help()
    sys.exit(0)

app = App(args)
app.apply_args()
app.run()
