'use strict';
{
    const toggleNavSidebar = document.getElementById('toggle-nav-sidebar');
    let matches = false;
    if (toggleNavSidebar !== null) {
        const navSidebar = document.getElementById(window.filter_applist_element || 'nav-sidebar');
        const main = document.getElementById('main');
        let navSidebarIsOpen = localStorage.getItem('django.admin.navSidebarIsOpen');
        if (navSidebarIsOpen === null) {
            navSidebarIsOpen = 'true';
        }
        main.classList.toggle('shifted', navSidebarIsOpen === 'true');
        navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);

        toggleNavSidebar.addEventListener('click', function() {
            if (navSidebarIsOpen === 'true') {
                navSidebarIsOpen = 'false';
            } else {
                navSidebarIsOpen = 'true';
            }
            localStorage.setItem('django.admin.navSidebarIsOpen', navSidebarIsOpen);
            main.classList.toggle('shifted');
            navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);
        });
    }

    function initSidebarQuickFilterv2() {
        const tables = [];
        const navSidebar = document.getElementById(window.filter_applist_element || 'nav-sidebar');
        if (!navSidebar) {
            return;
        }

        navSidebar.querySelectorAll('table').forEach((eltable) => {
            var table_options = {el: eltable, options: []};
            eltable.querySelectorAll('th[scope=row] a').forEach((container) => {
                table_options.options.push({title: container.innerHTML, node: container});
            });
            tables.push(table_options);
        });

        function checkValuev2(event) {
            let filterValue = event.target.value;
            if (filterValue) {
                filterValue = filterValue.toLowerCase();
            }
            if (event.key === 'Escape') {
                filterValue = '';
                event.target.value = ''; // clear input
            }
            for (const t of tables) {
                let matches = false;
                for (const o of t.options) {
                    let displayValue = '';
                    if (filterValue) {
                        const title_test = o.title.toLowerCase().indexOf(filterValue) === -1;
                        const href_test = o.node.href && o.node.href.includes(filterValue);
                        if (title_test && !href_test) {
                            displayValue = 'none';
                        } else {
                            matches = true;
                        }
                    }
                    // show/hide parent <TR>
                    o.node.parentNode.parentNode.style.display = displayValue;
                }
                if(filterValue.length){
                    t.el.parentNode.style.display = matches ? '' : 'none';
                } else {
                    t.el.parentNode.style.display = '';
                }
            }
            if (!filterValue || matches) {
                event.target.classList.remove('no-results');
            } else {
                event.target.classList.add('no-results');
            }
            sessionStorage.setItem('django.admin.navSidebarFilterValue', filterValue);
        }

        const nav = document.getElementById(window.filter_input_element || 'nav-filter');
        nav.addEventListener('change', checkValuev2, false);
        nav.addEventListener('input', checkValuev2, false);
        nav.addEventListener('keyup', checkValuev2, false);

        const storedValue = sessionStorage.getItem('django.admin.navSidebarFilterValue');
        if (storedValue) {
            nav.value = storedValue;
            checkValuev2({target: nav, key: ''});
        }
    }
    window.initSidebarQuickFilter = initSidebarQuickFilterv2;
    initSidebarQuickFilterv2();
}
