from django import template

class LanguageMiddleware(object):
    """
    Returns an alternative right to left version of each template if it exists 
    """
    def get_rtl_version_of_template(self, template_name):
        split_template_name = template_name.split('.')
        if len(split_template_name) < 2:
            return template_name
        rtl_template_name = "{0}.rtl.{1}".format(template_name.split('.')[0],
                                                 template_name.split('.')[1])
        try:
            template.loader.get_template(rtl_template_name)
        except template.TemplateDoesNotExist:
            return template_name
        else:
            return rtl_template_name
    
    def process_template_response(self, request, response):
        if request.LANGUAGE_CODE == 'ar':
            if isinstance(response.template_name, basestring):
                response.template_name = self.get_rtl_version_of_template(response.template_name)
            else:
                rtl_template_names  = [self.get_rtl_version_of_template(template_name) for template_name in response.template_name]
                response.template_name = rtl_template_names
        return response
