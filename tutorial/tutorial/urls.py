from django.conf.urls import patterns, include, url

urlpatterns = [
	url(r'^', include('snippets.urls')),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
