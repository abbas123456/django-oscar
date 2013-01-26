from django.conf import settings
from django.template.base import TemplateSyntaxError, Library, token_kwargs, Variable
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.template import loader_tags as django_loader_tags

register = Library()

def get_rtl_version_of_template(template_name):
    rtl_template_name = "{0}.rtl.{1}".format(template_name.split('.')[0],
                                             template_name.split('.')[1])
    try:
        get_template(rtl_template_name)
    except TemplateDoesNotExist:
        return template_name
    else:
        return rtl_template_name


class ExtendsNode(django_loader_tags.ExtendsNode):

    def get_parent(self, context):
        parent = self.parent_name.resolve(context)
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name.filters or\
                    isinstance(self.parent_name.var, Variable):
                error_msg += " Got this from the '%s' variable." %\
                    self.parent_name.token
            raise TemplateSyntaxError(error_msg)
        if context['LANGUAGE_CODE'] == 'ar':
            parent = get_rtl_version_of_template(parent)
        if hasattr(parent, 'render'):
            return parent # parent is a Template object
        return get_template(parent)


class ConstantIncludeNode(django_loader_tags.BaseIncludeNode):

    def __init__(self, template_path, *args, **kwargs):
        super(ConstantIncludeNode, self).__init__(*args, **kwargs)
        self.template_path = template_path
        try:
            t = get_template(template_path)
            self.template = t
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            self.template = None

    def render(self, context):
        if not self.template:
            return ''
        if context['LANGUAGE_CODE'] == 'ar':
            self.template = get_template(get_rtl_version_of_template(self.template_path))
        return self.render_template(self.template, context)


class IncludeNode(django_loader_tags.BaseIncludeNode):

    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            if context['LANGUAGE_CODE'] == 'ar':
                template_name = get_rtl_version_of_template(template_name)
            template = get_template(template_name)
            return self.render_template(template, context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''

@register.tag('extends')
def do_extends(parser, token):
    """
    Signal that this template extends a parent template.

    This tag may be used in two ways: ``{% extends "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% extends variable %}`` uses the value of ``variable`` as either the
    name of the parent template to extend (if it evaluates to a string) or as
    the parent tempate itelf (if it evaluates to a Template object).
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return ExtendsNode(nodelist, parent_name)

@register.tag('include')
def do_include(parser, token):
    """
    Loads a template and renders it with the current context. You can pass
    additional context using keyword arguments.

    Example::

        {% include "foo/some_include" %}
        {% include "foo/some_include" with bar="BAZZ!" baz="BING!" %}

    Use the ``only`` argument to exclude the current context when rendering
    the included template::

        {% include "foo/some_include" only %}
        {% include "foo/some_include" with bar="1" only %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("%r tag takes at least one argument: the name of the template to be included." % bits[0])
    options = {}
    remaining_bits = bits[2:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value
    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    path = bits[1]
    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ConstantIncludeNode(path[1:-1], extra_context=namemap,
                                   isolated_context=isolated_context)
    return IncludeNode(parser.compile_filter(bits[1]), extra_context=namemap,
                       isolated_context=isolated_context)