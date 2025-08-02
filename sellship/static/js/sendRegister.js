const buttons = {
    ebaySite: document.querySelector('#ebay-button'),
    otherSite: document.querySelector('#other-site-button')
}

const forms = {
    ebaySite: document.querySelector('#purchase-ebay-form'),
    otherSite: document.querySelector('#purchase-other-form')
}



function switchFormSite(formType) {
    switch(formType) {
        case 'ebay':
            if (forms.otherSite && forms.ebaySite && buttons.ebaySite && buttons.otherSite) {
                forms.ebaySite.classList.remove('hide-form');
                forms.otherSite.classList.add('hide-form');
                buttons.ebaySite.setAttribute('disabled', '')
                buttons.otherSite.removeAttribute('disabled')
            }
            break;

        case 'other':
            if (forms.otherSite && forms.ebaySite && buttons.ebaySite && buttons.otherSite) {
                forms.ebaySite.classList.add('hide-form');
                forms.otherSite.classList.remove('hide-form');
                buttons.otherSite.setAttribute('disabled', '')
                buttons.ebaySite.removeAttribute('disabled')
            }
            break;
    }
}


if (buttons.ebaySite) {
    buttons.ebaySite.addEventListener('click', () => {
        switchFormSite('ebay');
    });
}

if (buttons.otherSite) {
    buttons.otherSite.addEventListener('click', () => {
        switchFormSite('other');
    });
}


// --------------------------------- ПР+РОВЕРИТЬ И ПОМЕНЯТЬ ТО ЧТО НЕ ТАК

const STATUS_TYPES = ["form-buy", "form-massage", "form-offer"];

function switchFormStatus(statusType) {
    // Скрываем все формы
    STATUS_TYPES.forEach(type => {
        const form = document.getElementById(type);
        if (form) form.classList.add("hide-form");
    });

    // Показываем нужную форму
    const selectedForm = document.getElementById(statusType);
    if (selectedForm) selectedForm.classList.remove("hide-form");
}



document.querySelectorAll(".status-button").forEach(button => {
    button.addEventListener("click", () => {
        const selected = button.getAttribute("data-option");
        if (selected) switchFormStatus(selected);
    });
});

// --------------------------------- Делали вместе, проверить
const input = document.getElementById('autoArticleComplete');
const list = document.getElementById('autoArticleComplete-list');
let currentFocus = -1;

input.addEventListener('input', function() {
  const val = this.value.trim();
  if (!val) {
    closeList();
    return;
  }

  // Запрос к API с поисковым значением
  fetch(`/api/articles/?q=${encodeURIComponent(val)}`)
    .then(response => response.json())
    .then(data => {
      // data — ожидается массив строк или объектов с нужным свойством для отображения
      renderList(data);
    })
    .catch(() => closeList());
});

function renderList(items) {
  closeList();
  if (!items.length) return;
  list.style.display = 'block';

  items.forEach((item, i) => {
    const div = document.createElement('div');
    div.style.padding = '5px';
    div.style.cursor = 'pointer';

    if (typeof item === 'string') {
      div.textContent = item;
    } else if (item.similar_article) {
      div.textContent = `${item.similar_article} | ${item.id}`;
    } else {
      div.textContent = `${item.id}`;
    }


    if (typeof item !== 'string') {
      div.dataset.id = item.id;
    }

    div.addEventListener('click', () => {
      input.value = div.dataset.id;
      closeList();
    });

    list.appendChild(div);
  });
}

// Закрыть список
function closeList() {
  list.innerHTML = '';
  list.style.display = 'none';
  currentFocus = -1;
}

// Обработка клавиш для навигации по списку
input.addEventListener('keydown', function(e) {
  const items = list.getElementsByTagName('div');
  if (!items.length) return;

  if (e.key === 'ArrowDown') {
    currentFocus++;
    if (currentFocus >= items.length) currentFocus = 0;
    setActive(items);
    e.preventDefault();
  } else if (e.key === 'ArrowUp') {
    currentFocus--;
    if (currentFocus < 0) currentFocus = items.length - 1;
    setActive(items);
    e.preventDefault();
  } else if (e.key === 'Enter') {
    if (currentFocus > -1) {
      e.preventDefault();
      items[currentFocus].click();
    }
  }
});

function setActive(items) {
  for (let i = 0; i < items.length; i++) {
    items[i].style.backgroundColor = '';
  }
  if (currentFocus > -1 && items[currentFocus]) {
    items[currentFocus].style.backgroundColor = '#e9e9e9';
  }
}

// Закрыть список при клике вне инпута и списка
document.addEventListener('click', function(e) {
  if (e.target !== input && e.target.parentNode !== list) {
    closeList();
  }
});

//-----------