from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from snippets import views 

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'snippets', views.SnippetViewSet)
router.register(r'snippetdata', views.SnippetDataViewSet)

urlpatterns = [
	url(r'^', include(router.urls)),
	url(r'^snippetsearch/$', views.SnippetSearchList.as_view()),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]