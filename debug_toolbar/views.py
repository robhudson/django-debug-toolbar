from django.http import JsonResponse
from django.utils.html import escape
from django.utils.translation import gettext as _

from debug_toolbar.decorators import render_with_toolbar_language, require_show_toolbar
from debug_toolbar.panels.history import HistoryPanel
from debug_toolbar.panels.sql import SQLPanel
from debug_toolbar.panels.timer import TimerPanel
from debug_toolbar.store import get_store
from debug_toolbar.toolbar import DebugToolbar


@require_show_toolbar
@render_with_toolbar_language
def render_panel(request):
    """Render the contents of a panel"""
    toolbar = DebugToolbar.fetch(request.GET["request_id"], request.GET["panel_id"])
    if toolbar is None:
        content = _(
            "Data for this panel isn't available anymore. "
            "Please reload the page and retry."
        )
        content = "<p>%s</p>" % escape(content)
        scripts = []
    else:
        panel = toolbar.get_panel_by_id(request.GET["panel_id"])
        content = panel.content
        scripts = panel.scripts
    return JsonResponse({"content": content, "scripts": scripts})


@require_show_toolbar
def api_requests(request):
    """Return a JSON representation of the requests in the store.

    This always contains the `request_id`, but may include other meta data
    depending on the panels that have been enabled.

    """
    store = get_store()
    if not store:
        return JsonResponse({"requests": []})

    requests = []
    for request_id in reversed(store.request_ids()):
        history_stats = store.panel(request_id, HistoryPanel.panel_id)
        timing_stats = store.panel(request_id, TimerPanel.panel_id)
        sql_stats = store.panel(request_id, SQLPanel.panel_id)
        request = {
            "request_id": request_id,
        }
        if history_stats:
            request.update(history_stats)
        if timing_stats:
            request.update(
                {
                    "total_time": timing_stats["total_time"],
                }
            )
        if sql_stats:
            request.update(
                {
                    "sql_time": sql_stats["sql_time"],
                    "sql_queries": len(sql_stats["queries"]),
                }
            )
        requests.append(request)

    return JsonResponse({"requests": requests})


@require_show_toolbar
def api_request(request, request_id):
    """Return a JSON representation of all the stored data for the given `request_id`."""
    store = get_store()
    if not store:
        return JsonResponse({"requests": []})

    data = {}
    for panel, panel_data in store.panels(request_id):
        data[panel.removesuffix("Panel")] = panel_data

    return JsonResponse({"data": data})
