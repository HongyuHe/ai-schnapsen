import sys
from kb import KB, Boolean, Integer, Constant

# Define our symbols
P = Boolean('P')
Q = Boolean('Q')
R = Boolean('R')

# Create P new knowledge base
kb = KB()

# KB
kb.add_clause(P, Q)
kb.add_clause(R,~Q)
kb.add_clause(~P,~R)

# ~alpha
kb.add_clause(P,~Q)
kb.add_clause(~P,Q)

# Print all models of the knowledge base
for model in kb.models():
    print(model)

# Print out whether the KB is satisfiable (if there are no models, it is not satisfiable)
print(kb.satisfiable())
