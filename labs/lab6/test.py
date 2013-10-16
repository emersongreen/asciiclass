from pyspark import SparkContext

import json
import time
import hashlib

print 'loading'
sc = SparkContext("spark://ec2-54-200-174-121.us-west-2.compute.amazonaws.com:7077", "Simple App")
# Replace `lay-k.json` with `*.json` to get a whole lot more data.
lay = sc.textFile('s3n://AKIAJFDTPC4XX2LVETGA:lJPMR8IqPw2rsVKmsSgniUd+cLhpItI42Z6DCFku@6885public/enron/lay-k.json')

json_lay = lay.map(lambda x: json.loads(x)).cache()
#print 'json lay count', json_lay.count()

#pairs = json_lay.flatMap(lambda x: [(x['sender'],term) for term in x['text'].split()])
#grouped = pairs.groupBy(lambda x: x)
#counts = [(x, len(y)) for (x, y) in grouped.collect()]
#para_counts = sc.parallelize(counts)
#print 'tf_counts', para_counts.take(5)

m = hashlib.md5()
email_term_pairs = json_lay.flatMap(lambda x: [(term, hashlib.sha224(x['text']).hexdigest()) for term in x['text'].split()])
email_term_pairs_distinct = email_term_pairs.distinct()
email_pairs_grouped = email_term_pairs_distinct.groupBy(lambda x: x[0])
idf_counts = [(x, len(y)) for (x, y) in email_pairs_grouped.collect()]
# idf_counts = email_pairs_grouped.flatMap(lambda x: (x[0], len(x[1])))
para_idf_counts = sc.parallelize(idf_counts)
print 'idf_counts', para_idf_counts.take(3)
#print email_pairs_grouped.collect()[:4]

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