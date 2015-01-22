from rest_framework import generics
from snippets.models import Snippet, SnippetData 
from snippets.serializers import SnippetSerializer, UserSerializer, SnippetDataSerializer
from django.contrib.auth.models import User
from rest_framework import permissions
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route

import json

@api_view(('GET',))
def api_root(request, format=None):
	return Response({
		'users': reverse('users', request=request, format=format),
		'snippets': reverse('snippetlist', request=request, format=format),
		'snippetdata': reverse('snippetdatalist', request=request, format=format),
		'snippetsearch': reverse('snippetsearch', request=request, format=format)
	})

class SnippetViewSet(viewsets.ModelViewSet):
	queryset = Snippet.objects.all()
	serializer_class = SnippetSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)

	@detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
	def highlight(self, request, *args, **kwargs):
		snippet = self.get_object()
		return Response(snippet.highlighted)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class SnippetDataViewSet(viewsets.ModelViewSet):
	queryset = SnippetData.objects.all()
	serializer_class = SnippetDataSerializer

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

class SnippetSearchList(generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

	def compare_values(self, op, value1, value2, units1, units2):
		""" Compare two values, using the given op and provided units.
		"""
		if value1 is None or value2 is None:
			print "Value1 or Value2 are None"
			return False
		try:
			#commented out for now
			#u1 = units.first(name=units1)
			#u2 = units.first(name=units2)

			#value1 = float(value1) * (u1.conversion_to_SI if u1 else 1)
			#value2 = float(value2) * (u2.conversion_to_SI if u2 else 1)

			if op == 'gt' or op == '>':
				return value1 > value2
			elif op == 'gte' or op == '>=':
				return value1 >= value2
			elif op == 'lt' or op == '<':
				return value1 < value2
			elif op == 'lte' or op == '<=':
				return value1 <= value2
			elif op == 'ne' or op == 'neg' or op == '!=':
				return value1 != value2
			else:
				return value1 == value2
		except:
			print "comparison error"
			return False

	def get_queryset(self):
		queryset = SnippetData.objects.all()
		#testing on http://127.0.0.1:8000/snippetsearch/?q={%22filters%22:[{%22name%22:%22peak_power%22,%20%22op%22:%22te%22,%20%22val%22:%2220%22,%22units%22:%22W%22}]}	%22 == "	
		q = self.request.query_params.get('q', None)
		print q
		if q:
			#process filters
			filters = json.loads(q)['filters']
			filter_length = len(filters)
			counter = 0

			while counter < filter_length:
				#find snippet data based on name
				results = []
				snippet_data = queryset.filter(field_name=filters[counter]['name'])
				print snippet_data
				#perform adjacent comparisons if there are enough filters to warrant it
				do_adjacent_comparisons = counter + 1 < filter_length and \
					filters[counter]['name'] == filters[counter + 1]['name']

				for result in snippet_data:
					#test a range of filters using field_value
					compare1 = self.compare_values(filters[counter]['op'],
                                          result.field_value,
                                          filters[counter]['value'],
                                          result.units,
                                          filters[counter]['units'])
					if do_adjacent_comparisons == True:
						compare2 = self.compare_values(filters[counter + 1]['op'],
												result.field_value,
												filters[counter + 1]['value'],
												result.units,
												filters[counter + 1]['units'])
						if compare1 and compare2:
							results.append(result.snippet)
					else:
						if compare1:
							results.append(result.snippet)
				counter += 1
				if do_adjacent_comparisons:
					counter += 1
		return results
	serializer_class = SnippetSerializer