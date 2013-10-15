from pyspark import SparkContext

import json
import time

print 'loading'
sc = SparkContext("spark://ec2-54-200-174-121.us-west-2.compute.amazonaws.com:7077", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:lJPMR8IqPw2rsVKmsSgniUd+cLhpItI42Z6DCFku@6885public/enron/lay-k.json')

json_lay = lay.map(lambda x: json.loads(x)).cache()
print 'json lay count', json_lay.count()

pairs = json_lay.flatMap(lambda x: [(x['sender'],term) for term in x['text'].split()])
print 'pairs', pairs.take(2)
counts = pairs.countByValue()
print 'counts', counts



################
# all_words = json_lay.flatMap(lambda x: x['text'].split())
# words = all_words.distinct()

# for word in words.collect()]

# json_lay.map(lambda x: 
####################
email_term_pairs = json_lay.flatMap(lambda x: [(term,x) for term in x['text'].split()])
#print 'email_term_pairs', email_term_pairs.take(1)

group_email_term_pairs = email_term_pairs.groupBy(lambda x: x[0])
#print 'group_email_term_pairs', group_email_term_pairs.take(1)

dist = group_email_term_pairs.flatMap(lambda x: x[0],len(x[1]))
print 'dist', dist.take(1)


filtered_lay = json_lay.filter(lambda x: 'chairman' in x['text'].lower())
print 'lay filtered to chairman', filtered_lay.count()

to_list = json_lay.flatMap(lambda x: x['to'])
print 'to_list', to_list.take(5)

#grab senders
#pairs  = json_lay.map(lambda x: {'term': term, 'author': x['sender']} for term in x['text'])
		# pairs = json_lay.flatMap(lambda x: [(x['sender'],term) for term in x['text'].split()])
		# groups = pairs.groupBy(lambda x: x)
		# print groups.take(1)
		# counts = pairs.map(lambda x: (x[0],len(x[1])))
#sender_group = json_lay.groupBy(lambda x: x['sender'])
#sender_group = json_lay.map(lambda x: x[])

#sender_message = [[(group[0],elem) for elem in group[1]] for group in result]
#sender_terms = 
#senders = json_lay.map(lambda x: x['sender']).distinct()
#collected = senders.collect()
		# print 'pairs_list', counts.take(3)
#terms = json_lay.filter(lambda x: _ in x['text'].lower())
#flat = terms.flatMap(lambda x: x)

		# counted_values = to_list.countByValue()
# Uncomment the next line to see a dictionary of every `to` mapped to
# the number of times it appeared.
#print 'counted_values', counted_values

# How to use a join to combine two datasets.
frequencies = sc.parallelize([('a', 2), ('the', 3)])
inverted_index = sc.parallelize([('a', ('doc1', 5)), ('the', ('doc1', 6)), ('cats', ('doc2', 1)), ('the', ('doc2', 2))])

# See also rightOuterJoin and leftOuterJoin.
join_result = frequencies.join(inverted_index)

# If you don't want to produce something as confusing as the next
# line's [1][1][0] nonesense, represent your data as dictionaries with
# named fields :).
multiplied_frequencies = join_result.map(lambda x: (x[0], x[1][1][0], x[1][0]*x[1][1][1]))
print 'term-document weighted frequencies', multiplied_frequencies.collect()