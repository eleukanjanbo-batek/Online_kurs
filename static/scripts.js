document.addEventListener('DOMContentLoaded', () => {
    // Sahifa yuklanganda localStorage dan holatni tekshiramiz
    const savedChecks = JSON.parse(localStorage.getItem('calledUsers') || '{}');

    Object.keys(savedChecks).forEach(id => {
        const checkbox = document.getElementById('check-' + id);
        const row = document.getElementById('row-' + id);

        if (checkbox && row && savedChecks[id]) {
            checkbox.checked = true;
            row.classList.add('done-row');
        }
    });
});

function checkCall(id) {
    const checkbox = document.getElementById('check-' + id);
    const row = document.getElementById('row-' + id);
    let savedChecks = JSON.parse(localStorage.getItem('calledUsers') || '{}');

    if (checkbox.checked) {
        row.classList.add('done-row');
        savedChecks[id] = true;
    } else {
        row.classList.remove('done-row');
        delete savedChecks[id];
    }
    localStorage.setItem('calledUsers', JSON.stringify(savedChecks));
}