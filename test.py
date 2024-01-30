from fuzzywuzzy import fuzz

str1 = "Shee"
str2 = "Shika"

# Calculate similarity score
similarity_score = fuzz.ratio(str1, str2)

# Print the similarity score
print("Similarity Score:", similarity_score)