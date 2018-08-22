import os
from . import config, logging, proxy_fix, request_id, formats, filters, errors
from flask_script import Manager, Server


def init_app(
        application,
        config_object,
        bootstrap=None,
        data_api_client=None,
        db=None,
        login_manager=None,
        search_api_client=None,
):

    application.config.from_object(config_object)
    if hasattr(config_object, 'init_app'):
        config_object.init_app(application)

    # all belong to dmutils
    config.init_app(application)
    logging.init_app(application)
    proxy_fix.init_app(application)
    request_id.init_app(application)

    if bootstrap:
        bootstrap.init_app(application)
    if data_api_client:
        data_api_client.init_app(application)
    if db:
        db.init_app(application)
    if login_manager:
        login_manager.init_app(application)
    if search_api_client:
        search_api_client.init_app(application)

    @application.after_request
    def add_header(response):
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # Make filters accessible in templates.
    application.add_template_filter(filters.capitalize_first)
    application.add_template_filter(filters.format_links)
    application.add_template_filter(filters.nbsp)
    application.add_template_filter(filters.smartjoin)
    application.add_template_filter(filters.preserve_line_breaks)
    # Make select formats available in templates.
    application.add_template_filter(formats.dateformat)
    application.add_template_filter(formats.datetimeformat)
    application.add_template_filter(formats.datetodatetimeformat)
    application.add_template_filter(formats.shortdateformat)
    application.add_template_filter(formats.timeformat)
    application.add_template_filter(formats.utcdatetimeformat)
    application.add_template_filter(formats.utctoshorttimelongdateformat)

    @application.context_processor
    def inject_global_template_variables():
        return dict(
            pluralize=pluralize,
            **(application.config['BASE_TEMPLATE_DATA'] or {}))

    # Register error handlers for CSRF errors and common error status codes
    application.register_error_handler(400, errors.csrf_handler)
    application.register_error_handler(401, errors.redirect_to_login)
    application.register_error_handler(403, errors.redirect_to_login)
    application.register_error_handler(404, errors.render_error_page)
    application.register_error_handler(410, errors.render_error_page)
    application.register_error_handler(503, errors.render_error_page)
    application.register_error_handler(500, errors.render_error_page)


def pluralize(count, singular, plural):
    return singular if count == 1 else plural


def get_extra_files(paths):
    for path in paths:
        for dirname, dirs, files in os.walk(path):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    yield filename


def init_manager(application, port, extra_directories=()):

    manager = Manager(application)

    extra_files = list(get_extra_files(extra_directories))

    logging.logger.debug("Watching {} extra files".format(len(extra_files)))

    manager.add_command(
        "runserver",
        Server(port=port, extra_files=extra_files)
    )

    def print_route(rule):
        print("{:10} {}".format(", ".join(rule.methods - set(['OPTIONS', 'HEAD'])), rule.rule))

    @manager.command
    def list_routes():
        """List URLs of all application routes."""
        for rule in sorted(manager.app.url_map.iter_rules(), key=lambda r: r.rule):
            if rule.endpoint.startswith("external"):
                continue
            print_route(rule)

    @manager.command
    def list_external_routes():
        """List URLs of all external routes."""
        for rule in sorted(manager.app.url_map.iter_rules(), key=lambda r: r.rule):
            if rule.endpoint.startswith("external"):
                print_route(rule)

    return manager
