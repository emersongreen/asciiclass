from pyspark import SparkContext

import json
import time
import hashlib
import math
import re

print 'loading'
sc = SparkContext("spark://ec2-54-200-174-121.us-west-2.compute.amazonaws.com:7077", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:lJPMR8IqPw2rsVKmsSgniUd+cLhpItI42Z6DCFku@6885public/enron/lay-k.json')

# Load JSON
json_lay = lay.map(lambda x: json.loads(x)).cache()

# Compute TF
pairs = json_lay.flatMap(lambda x: [(x['sender'], term.lower()) for term in x['text'].split()]).countByValue().items()
pair_map = sc.parallelize(pairs)
tf_out = pair_map.map(lambda x: ( x[0][1], (x[0][0], x[1])))
print 'tf_counts', tf_out.take(10)

# Compute IDF
email_term_pairs = json_lay.flatMap(lambda x: [(term.lower(), hashlib.sha224(x['text']).hexdigest()) for term in x['text'].split()])
email_term_pairs_distinct = email_term_pairs.distinct()
email_pairs_grouped = email_term_pairs_distinct.groupBy(lambda x: x[0], numPartitions=500)
numdocs = json_lay.count()
idf_out = email_pairs_grouped.map(lambda x: ( x[0], math.log(numdocs/ float(len(x[1])))))
print 'idf_counts', idf_out.take(10)

# Join the two RDD's and compute score
join_ifidf = tf_out.join(idf_out, numPartitions=500)
join_map = join_ifidf.map(lambda x: ( (x[0], x[1][0][0], x[1][0][1]*x[1][1] )))
print 'join', join_map.take(10)

# Sender disambiguation

filter_ken = join_map.filter(lambda x: re.match(r'(kenneth|lay).*', x[1]))
print 'ken', sorted(filter_ken.collect(), key=lambda x: x[2], reverse=True)[:10]

#filter_jeff = join_map.filter(lambda x: re.match(r'(jeff|skilling).*', x[1]))
#filter_andrew = join_map.filter(lambda x: re.match(r'(andrew|fastow).*', x[1]))



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