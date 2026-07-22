"use strict";
/*
 * volt.js — adaptado del tema Volt (Themesberg) para este proyecto.
 * Se protegieron con comprobaciones "typeof X !== 'undefined'" las
 * llamadas a librerias opcionales (SweetAlert2, SmoothScroll, Chartist,
 * Glide, noUiSlider, countUp, Datepicker) que no se cargan en este
 * proyecto, para que su ausencia no rompa el resto del script.
 */
const d = document;
d.addEventListener("DOMContentLoaded", function (event) {

    if (typeof Swal !== "undefined") {
        Swal.mixin({
            customClass: {
                confirmButton: 'btn btn-primary me-3',
                cancelButton: 'btn btn-gray'
            },
            buttonsStyling: false
        });
    }

    var themeSettingsEl = document.getElementById('theme-settings');
    var themeSettingsExpandEl = document.getElementById('theme-settings-expand');

    if (themeSettingsEl && themeSettingsExpandEl && typeof bootstrap !== "undefined") {
        var themeSettingsCollapse = new bootstrap.Collapse(themeSettingsEl, {
            show: true,
            toggle: false
        });

        if (window.localStorage.getItem('settings_expanded') === 'true') {
            themeSettingsCollapse.show();
            themeSettingsExpandEl.classList.remove('show');
        } else {
            themeSettingsCollapse.hide();
            themeSettingsExpandEl.classList.add('show');
        }

        themeSettingsEl.addEventListener('hidden.bs.collapse', function () {
            themeSettingsExpandEl.classList.add('show');
            window.localStorage.setItem('settings_expanded', false);
        });

        themeSettingsExpandEl.addEventListener('click', function () {
            themeSettingsExpandEl.classList.remove('show');
            window.localStorage.setItem('settings_expanded', true);
            setTimeout(function () {
                themeSettingsCollapse.show();
            }, 300);
        });
    }

    const breakpoints = { sm: 540, md: 720, lg: 960, xl: 1140 };

    var sidebar = document.getElementById('sidebarMenu');
    if (sidebar && d.body.clientWidth < breakpoints.lg) {
        sidebar.addEventListener('shown.bs.collapse', function () {
            document.querySelector('body').style.position = 'fixed';
        });
        sidebar.addEventListener('hidden.bs.collapse', function () {
            document.querySelector('body').style.position = 'relative';
        });
    }

    var iconNotifications = d.querySelector('.notification-bell');
    if (iconNotifications) {
        iconNotifications.addEventListener('shown.bs.dropdown', function () {
            iconNotifications.classList.remove('unread');
        });
    }

    if (typeof bootstrap !== "undefined") {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    if (typeof Datepicker !== "undefined") {
        var datepickers = [].slice.call(d.querySelectorAll('[data-datepicker]'));
        datepickers.map(function (el) {
            return new Datepicker(el, { buttonClass: 'btn' });
        });
    }

    if (typeof Chartist !== "undefined" && d.querySelector('.ct-chart-sales-value')) {
        new Chartist.Line('.ct-chart-sales-value', {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            series: [[0, 10, 30, 40, 80, 60, 100]]
        }, {
            low: 0, showArea: true, fullWidth: true,
            plugins: [Chartist.plugins.tooltip()],
            axisX: { position: 'end', showGrid: true },
            axisY: { showGrid: false, showLabel: false, labelInterpolationFnc: function (value) { return '$' + (value / 1) + 'k'; } }
        });
    }

    if (typeof Chartist !== "undefined" && d.querySelector('.ct-chart-ranking')) {
        var chart = new Chartist.Bar('.ct-chart-ranking', {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            series: [[1, 5, 2, 5, 4, 3], [2, 3, 4, 8, 1, 2]]
        }, {
            low: 0, showArea: true,
            plugins: [Chartist.plugins.tooltip()],
            axisX: { position: 'end' },
            axisY: { showGrid: false, showLabel: false, offset: 0 }
        });

        chart.on('draw', function (data) {
            if (data.type === 'line' || data.type === 'area') {
                data.element.animate({
                    d: {
                        begin: 2000 * data.index,
                        dur: 2000,
                        from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
                        to: data.path.clone().stringify(),
                        easing: Chartist.Svg.Easing.easeOutQuint
                    }
                });
            }
        });
    }

    if (typeof Chartist !== "undefined" && d.querySelector('.ct-chart-traffic-share')) {
        var pieData = { series: [70, 20, 10] };
        var sum = function (a, b) { return a + b; };
        new Chartist.Pie('.ct-chart-traffic-share', pieData, {
            labelInterpolationFnc: function (value) {
                return Math.round(value / pieData.series.reduce(sum) * 100) + '%';
            },
            low: 0, high: 8, donut: true, donutWidth: 20, donutSolid: true,
            fullWidth: false, showLabel: false,
            plugins: [Chartist.plugins.tooltip()]
        });
    }

    if (d.getElementById('loadOnClick')) {
        d.getElementById('loadOnClick').addEventListener('click', function () {
            var button = this;
            var loadContent = d.getElementById('extraContent');
            var allLoaded = d.getElementById('allLoadedText');

            button.classList.add('btn-loading');
            button.setAttribute('disabled', 'true');

            setTimeout(function () {
                if (loadContent) loadContent.style.display = 'block';
                button.style.display = 'none';
                if (allLoaded) allLoaded.style.display = 'block';
            }, 1500);
        });
    }

    if (typeof SmoothScroll !== "undefined") {
        new SmoothScroll('a[href*="#"]', { speed: 500, speedAsDuration: true });
    }

    if (d.querySelector('.current-year')) {
        d.querySelector('.current-year').textContent = new Date().getFullYear();
    }

    if (typeof Glide !== "undefined") {
        if (d.querySelector('.glide')) {
            new Glide('.glide', { type: 'carousel', startAt: 0, perView: 3 }).mount();
        }
        if (d.querySelector('.glide-testimonials')) {
            new Glide('.glide-testimonials', { type: 'carousel', startAt: 0, perView: 1, autoplay: 2000 }).mount();
        }
        if (d.querySelector('.glide-clients')) {
            new Glide('.glide-clients', { type: 'carousel', startAt: 0, perView: 5, autoplay: 2000 }).mount();
        }
        if (d.querySelector('.glide-news-widget')) {
            new Glide('.glide-news-widget', { type: 'carousel', startAt: 0, perView: 1, autoplay: 2000 }).mount();
        }
        if (d.querySelector('.glide-autoplay')) {
            new Glide('.glide-autoplay', { type: 'carousel', startAt: 0, perView: 3, autoplay: 2000 }).mount();
        }
    }

    var billingSwitchEl = d.getElementById('billingSwitch');
    if (billingSwitchEl && typeof countUp !== "undefined") {
        const countUpStandard = new countUp.CountUp('priceStandard', 99, { startVal: 199 });
        const countUpPremium = new countUp.CountUp('pricePremium', 199, { startVal: 299 });

        billingSwitchEl.addEventListener('change', function () {
            if (billingSwitchEl.checked) {
                countUpStandard.start();
                countUpPremium.start();
            } else {
                countUpStandard.reset();
                countUpPremium.reset();
            }
        });
    }
});
