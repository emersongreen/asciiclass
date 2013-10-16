from pyspark import SparkContext

import json
import time
import hashlib
import math

print 'loading'
sc = SparkContext("spark://ec2-54-200-174-121.us-west-2.compute.amazonaws.com:7077", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:lJPMR8IqPw2rsVKmsSgniUd+cLhpItI42Z6DCFku@6885public/enron/lay-k.json')

json_lay = lay.map(lambda x: json.loads(x)).cache()
#print 'json lay count', json_lay.count()

pairs = json_lay.flatMap(lambda x: [(x['sender'], term.lower()) for term in x['text'].split()]).countByValue().items()
pair_map = sc.parallelize(pairs)
tf_out = pair_map.map(lambda x: ( x[0][1], (x[0][0], x[1])))
#grouped = pairs.groupBy(lambda x: x)
#counts = [(x, len(y)) for (x, y) in grouped.collect()]
#para_counts = sc.parallelize(counts)
print 'tf_counts', tf_out.take(10)

email_term_pairs = json_lay.flatMap(lambda x: [(term.lower(), hashlib.sha224(x['text']).hexdigest()) for term in x['text'].split()])
email_term_pairs_distinct = email_term_pairs.distinct()
email_pairs_grouped = email_term_pairs_distinct.groupBy(lambda x: x[0])
numdocs = json_lay.count()
idf_out = email_pairs_grouped.map(lambda x: ( x[0], math.log(numdocs/ float(len(x[1])))))
#idf_counts = [(x, len(y)) for (x, y) in email_pairs_grouped.collect()]
# idf_counts = email_pairs_grouped.flatMap(lambda x: (x[0], len(x[1])))
#para_idf_counts = sc.parallelize(idf_counts)
print 'idf_counts', idf_out.take(10)
#print email_pairs_grouped.collect()[:4]

join_ifidf = tf_out.join(idf_out)
join_map = join_ifidf.map(lambda x: ( (x[0], x[1][0][0], x[1][0][1]*x[1][1] )))
print 'join', join_map.take(10)
#get_scores = join_ifidf.map(lambda x: ())

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