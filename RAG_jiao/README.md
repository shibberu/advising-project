## Existing Problems & Observations

### Confusion with similar concepts
Mistral-7b can't tell the difference between some similar concepts. For example, if the context contains only info about Japanese as a minor, but the question is asking about Japanese as a major (which is not a thing here at Rose), it might think that the info it has is about Japanese major and answer the question with that wrong info. 

### Bad at parallel structures
When the query contains parallel structures like "and" and "or," mistral-7b is more likely to make mistakes. This is especially true when the parallel phrases are key info. For example, "Do I need to take **CHEM 111 and CHEM 113** for a second major in civil engineering?"

### Irrelevant/Unhelpful context affects performance
It's not always a good idea to feed more context to mistral-7b. When there is too much irrelevant context, it's more likely to hallucinate.
This is also true if the context is related but not unhelpful. For example:

Q: Do I need to take CHEM 111 and CHEM 113 for a second major in civil engineering?

Context 1: <br>
  chunk 1: the csv with info about required courses for CE. <br>

Context 2: <br>
  chunk 1: the csv with info about required courses for CE. <br>
  chunk 2: something that mentions CHEM 111, but is not relevant to the query <br>
  chunk 3: something that mentions CHEM 111, but is not relevant to the query <br>

Mistral-7b will always answer the question correctly with context 1, but not with context 2

### About BGE reranker
It can assign a very low even negative score to a chunk with the most relevant information

## Credits
Created by Qingyuan Jiao. Contact jiaoq@rose-hulman.edu if you have any questions.
