function activate_tooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-coreui-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new coreui.Tooltip(tooltipTriggerEl));
};

function showToastMsg(msg) {
    $('#result-message-toast .toast-body').html(msg);
    const toast = document.getElementById('result-message-toast');
    const toastCoreUI = coreui.Toast.getOrCreateInstance(toast);
    toastCoreUI.show();
};

function updatePageSelector(num_pages, page_n) {
    let from, to;
    if(page_n <= 3) {
        from = 1;
        to = num_pages>=5 ? 5: num_pages;
    } else if(page_n >= num_pages-2) {
        from = num_pages >= 5? num_pages - 4: 1;
        to = num_pages;
    } else {
        from = page_n - 2;
        to = page_n + 2;
    }

    let page_selector = $('#upd2');
    page_selector.html('');
    page_selector.append(
        `<li class="page-item" id="first">
            <button type="button" class="page-link" href="first">&lt;&lt;</button>
        </li>
        <li class="page-item" id="previous">
            <button type="button" class="page-link" href="previous">&lt;</button>
        </li>`
    );
    for(let i = from; i <= to; i++) {
        page_selector.append(
            `<li class="page-item${(i==page_n?' active':'')}" id="${i}">
                <button type="button" class="page-link" href="${i}">${i}</button>
            </li>`
        );
    }
    page_selector.append(
        `<li class="page-item" id="next">
            <button type="button" class="page-link" href="next">&gt;</button>
        </li>
        <li class="page-item" id="last">
            <button type="button" class="page-link" href="last">&gt;&gt;</button>
        </li>`
    );
};