from functools import wraps

from django.shortcuts import redirect


def mayorista_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, "perfil_mayorista"):
            return redirect("portal_login_mayorista")
        request.mayorista = request.user.perfil_mayorista
        return view_func(request, *args, **kwargs)

    return wrapper


def vendedor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, "perfil_vendedor"):
            return redirect("portal_login_vendedor")
        vendedor = request.user.perfil_vendedor
        if vendedor.primer_login and view_func.__name__ != "cambiar_password":
            return redirect("portal_vendedor_cambiar_password")
        request.vendedor = vendedor
        return view_func(request, *args, **kwargs)

    return wrapper


def tienda_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, "perfil_tienda"):
            return redirect("portal_login_tienda")
        request.tienda = request.user.perfil_tienda
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("portal_login_admin")
        return view_func(request, *args, **kwargs)

    return wrapper
