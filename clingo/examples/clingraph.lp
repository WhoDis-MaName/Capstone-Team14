% #include "overlap_identifier.lp".

node(cist3110; cist1600; csci1200; csci8456).

edge(cist1600,cist3110);
edge(csci1200,cist3110); 
edge(csci8456,cist3110); 
edge(cist3110,cist1600); 
edge(csci8456,cist1600); 
edge(cist3110,csci1200); 
edge(csci8456,csci1200); 
edge(cist3110,csci8456); 
edge(cist1600,csci8456); 
edge(csci1200,csci8456);

attr(graph, default, label, "Classes without conflict").

node(cist3110; cist1600; csci1200; csci8456).

attr(graph_nodes, default, style, filled).
attr(node, cist3110, label, "Advanced Composition For IS&T").
attr(node, cist1600, label, "Practical Scripting").
attr(node, csci1200, label, "CS Principles").
attr(node, csci8456, label, "Artificial Intelligence").