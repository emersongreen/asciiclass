import sys
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms
import math
import itertools
import operator

class TFIDF(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol
	OUTPUT_PROTOCOL = JSONValueProtocol

	# Map-reduce to count the occurence of each term/author pair
	def map_counts(self, key, email):
		# First let's count terms and authorss
	    for term in get_terms(email['text']):
	        yield {'term': term, 'author': email['sender']}, 1

	def reducer_counts(self, term_author_pair, howmany):
		# Reduce to find count
	    yield term_author_pair, sum(howmany)

	# Map to group the author/counts according to each term, reduce and calculate tfidf
	def mapper_by_term(self, term_author_pair, total):
		# map terms
	    yield term_author_pair['term'], {'author': term_author_pair['author'], 'total': total}

	def reducer_by_term(self, term, author_and_total):
		# Reduce to find ifidf
		alltotals, alltotals2 = itertools.tee(author_and_total)
		email_sum = 0
		for elem in alltotals:
			email_sum = email_sum + 1
		
		for data in alltotals2:
			term1 = data['total']
			calc_tfidf = term1 * math.log( 516893 / email_sum)
			yield data['author'], {'term': term, 'calc': calc_tfidf}

		# Final map_reduce combo to accomplish the calculations for lab questions
	def mapper_final(self, author, term_calc):
		yield author, term_calc


	def reducer_final(self, author, term_calc):
		# Need to find TFIDF counts for Kenneth Lay, Jeff Skilling, Andrew Fastow, Rebecca Mark-Jusbasche, Stephen Cooper
		author_list = ['kenneth.lay@enron.com', 'jeff.skilling@enron.com', 'andrew.fastow@enron.com']
		if author in author_list:
			term_dictionary = {}
			for item in term_calc:
				# Add all the terms and TFIDF counts to a dictionary
				term_dictionary[item['term']] = item['calc']
			
			value_list = [(value,key) for key, value in term_dictionary.items()]
			value_list.sort()
			#grab the 5 highest
			high_keys = [(v,k) for v, k in value_list[-5:]]
			yield None, {'author': author, 'high': high_keys}

	def steps(self):
		return [self.mr(mapper=self.map_counts, 
			reducer=self.reducer_counts),
			 self.mr(mapper=self.mapper_by_term,
			  reducer=self.reducer_by_term), 
			 self.mr(mapper=self.mapper_final, 
			 	reducer=self.reducer_final)]

if __name__ == '__main__':
        TFIDF.run()