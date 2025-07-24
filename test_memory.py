from relationship_agent.memory import Memory

mem = Memory()

import random

sample_memories = [
    "I went hiking in the mountains last summer.",
    "My favorite book is 'To Kill a Mockingbird'.",
    "I once met a famous actor at the airport.",
    "The smell of fresh coffee always wakes me up.",
    "I learned to ride a bicycle when I was six.",
    "Rainy days make me feel nostalgic.",
    "I enjoy painting landscapes in my free time.",
    "My best friend and I traveled to Japan together.",
    "I love listening to jazz music on Sunday mornings.",
    "Baking cookies with my grandmother is a cherished memory.",
    "The first time I saw the ocean, I was amazed.",
    "I adopted a stray cat during college.",
    "My favorite holiday is Halloween.",
    "I once got lost in a foreign city and found a hidden café.",
    "I enjoy stargazing on clear nights."
]

for memory in random.sample(sample_memories, 10):
    mem.add_memory(memory)
