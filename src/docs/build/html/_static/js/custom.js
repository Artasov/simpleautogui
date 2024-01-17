document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('li').forEach((li) => {
        const a = li.querySelector('a');
        if (a && (a.textContent.includes('Submodules') ||
            a.textContent.includes('Subpackages') ||
            a.textContent.includes('Module contents'))
        ) {
            const ul = li.querySelector(':scope > ul');
            if (ul) {
                while (ul.firstChild) {
                    li.parentNode.appendChild(ul.firstChild);
                }
                ul.remove();
            }
            li.remove();
        }
    });

    const moduleNames = document.querySelectorAll('.reference.internal');
    moduleNames.forEach((moduleName) => {
        let fullText = moduleName.textContent || moduleName.innerText;
        if (fullText.includes(' package') || fullText.includes(' module')) {
            fullText = fullText.replace('package', '').replace('module', '');
            moduleName.textContent = fullText.split('.').pop();
        }
    });

});