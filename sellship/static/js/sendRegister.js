const buttons = {
    ebaySite: document.querySelector('#ebay-button'),
    otherSite: document.querySelector('#other-site-button')
}

const forms = {
    ebaySite: document.querySelector('#purchase-ebay-form'),
    otherSite: document.querySelector('#purchase-other-form')
}

// Кнопка отправки
const submitButton = document.querySelector('#purchase-ebay-form button[type="submit"]');



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

function switchFormStatus(statusType, updateHash = true) {
    // Убираем активный класс со всех кнопок статуса
    document.querySelectorAll(".status-button").forEach(button => {
        button.classList.remove("active");
    });
    
    // Добавляем активный класс к выбранной кнопке
    const activeButton = document.querySelector(`[data-option="${statusType}"]`);
    if (activeButton) {
        activeButton.classList.add("active");
    }
    
    // Скрываем все формы
    STATUS_TYPES.forEach(type => {
        const form = document.getElementById(type);
        if (form) form.classList.add("hide-form");
    });

    // Показываем нужную форму
    const selectedForm = document.getElementById(statusType);
    if (selectedForm) selectedForm.classList.remove("hide-form");
    
    // Показываем кнопку отправки только если статус выбран
    if (submitButton) {
        submitButton.style.display = 'block';
    }
    
    // Обновляем URL с хэшем только если это не восстановление из URL
    if (updateHash) {
        updateURLHash(statusType);
    }
}

// Функция для обновления URL хэша
function updateURLHash(action) {
    const currentHash = window.location.hash;
    const newHash = `#action=${action}`;
    
    if (currentHash !== newHash) {
        window.location.hash = newHash;
    }
}

// Функция для получения действия из URL хэша
function getActionFromHash() {
    const hash = window.location.hash;
    const match = hash.match(/#action=([^&]+)/);
    return match ? match[1] : null;
}

// Функция для восстановления состояния из URL
function restoreStateFromURL() {
    const action = getActionFromHash();
    if (action && STATUS_TYPES.includes(action)) {
        switchFormStatus(action, false); // Не обновляем хэш при восстановлении
    }
}

// Функция для скрытия кнопки отправки
function hideSubmitButton() {
    if (submitButton) {
        submitButton.style.display = 'none';
    }
}

// Скрываем кнопку отправки при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    hideSubmitButton();
    
    // Инициализация плавающих labels
    initFloatingLabels();
    
        // Восстанавливаем состояние из URL
    restoreStateFromURL();
    
    // Обработчик изменения хэша в URL
    window.addEventListener('hashchange', function() {
        restoreStateFromURL();
    });
});




document.querySelectorAll(".status-button").forEach(button => {
    button.addEventListener("click", () => {
        const selected = button.getAttribute("data-option");
        if (selected) switchFormStatus(selected, true); // Обновляем хэш при клике
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
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // data — ожидается массив строк или объектов с нужным свойством для отображения
      renderList(data);
    })
    .catch(error => {
      closeList();
    });
});

function renderList(items) {
  closeList();
  if (!items.length) return;
  
  list.style.display = 'block';
  list.style.visibility = 'visible';

  items.forEach((item, i) => {
    const div = document.createElement('div');
    
    // Создаем структуру для отображения данных
    if (typeof item === 'string') {
      div.innerHTML = `<span class="article-text">${item}</span>`;
    } else if (item.similar_article) {
      div.innerHTML = `
        <span class="article-text">${item.similar_article}</span>
        <span class="article-id">ID: ${item.id}</span>
      `;
    } else {
      div.innerHTML = `
        <span class="article-text">Артикул</span>
        <span class="article-id">ID: ${item.id}</span>
      `;
    }

    if (typeof item !== 'string') {
      div.dataset.id = item.id;
    }

    div.addEventListener('click', () => {
      input.value = div.dataset.id || item;
      closeList();
    });

    div.addEventListener('mouseenter', () => {
      // Убираем активный класс со всех элементов
      list.querySelectorAll('div').forEach(el => el.classList.remove('active'));
      // Добавляем активный класс к текущему элементу
      div.classList.add('active');
    });

    list.appendChild(div);
  });
}

// Закрыть список
function closeList() {
  list.innerHTML = '';
  list.style.display = 'none';
  list.style.visibility = 'hidden';
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

// Функция для инициализации плавающих labels
function initFloatingLabels() {
    const floatingContainers = document.querySelectorAll('.floating-label-container');
    
    floatingContainers.forEach(container => {
        const input = container.querySelector('input, select, textarea');
        const label = container.querySelector('.floating-label');
        
        if (!input || !label) return;
        
        // Проверяем, есть ли уже значение при загрузке
        if (input.value && input.value !== '') {
            container.classList.add('has-value');
        }
        
        // Обработчик изменения значения
        input.addEventListener('change', function() {
            if (this.value && this.value !== '') {
                container.classList.add('has-value');
            } else {
                container.classList.remove('has-value');
            }
        });
        
        // Обработчик получения фокуса
        input.addEventListener('focus', function() {
            container.classList.add('focused');
        });
        
        // Обработчик потери фокуса
        input.addEventListener('blur', function() {
            container.classList.remove('focused');
            if (!this.value || this.value === '') {
                container.classList.remove('has-value');
            }
        });
        
        // Для select элементов также обрабатываем событие input
        if (input.tagName === 'SELECT') {
            input.addEventListener('input', function() {
                if (this.value && this.value !== '') {
                    container.classList.add('has-value');
                } else {
                    container.classList.remove('has-value');
                }
            });
        }
        
        // Для input элементов также обрабатываем событие input
        if (input.tagName === 'INPUT') {
            input.addEventListener('input', function() {
                if (this.value && this.value !== '') {
                    container.classList.add('has-value');
                } else {
                    container.classList.remove('has-value');
                }
            });
            
            // Специальная обработка для полей даты
            if (input.type === 'date') {
                input.addEventListener('change', function() {
                    if (this.value && this.value !== '') {
                        container.classList.add('has-value');
                    } else {
                        container.classList.remove('has-value');
                    }
                });
            }
        }
    });
}

