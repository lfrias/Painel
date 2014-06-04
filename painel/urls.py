from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'monitoring.views.home', name='home'),
    url(r'get_alarm$', 'monitoring.views.get_alarm', name='get_alarm'),
    url(r'salas$', 'monitoring.views.get_salas_html', name='salas'),
    url(r'condicoes-de-operacao$', 'monitoring.views.get_cond_op_html',
        name='condicoes_operacao'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
