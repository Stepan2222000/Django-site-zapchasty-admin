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
        submitButton.style.display = 'inline-flex';
    }
    
    // Обновляем URL с хэшем только если это не восстановление из URL
    if (updateHash) {
        updateURLHash(statusType);
    }
}

// Map between tab ids and status values expected by backend
const TAB_TO_STATUS = {
    'form-buy': 'КУПЛЕННО',
    'form-massage': 'НАПИСАЛИ',
    'form-offer': 'ОФФЕР'
};

function setHiddenStatusByTab(tabId) {
    const form = document.getElementById('purchase-ebay-form');
    if (!form) return;
    const hiddenStatus = form.querySelector('input[name="status"]');
    if (!hiddenStatus) return;
    const newStatus = TAB_TO_STATUS[tabId];
    if (newStatus) hiddenStatus.value = newStatus;
}

// Hook into status switch to update status input
const originalSwitchFormStatus = switchFormStatus;
switchFormStatus = function(statusType, updateHash = true) {
    originalSwitchFormStatus(statusType, updateHash);
    setHiddenStatusByTab(statusType);
};

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

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация плавающих labels
    initFloatingLabels();

    // Восстанавливаем состояние из URL
    restoreStateFromURL();

    // Если нет хэша в URL, устанавливаем статус "Куплено" по умолчанию
    if (!getActionFromHash()) {
        switchFormStatus('form-buy', false);
    } else {
        // Если есть хэш, устанавливаем активный класс на соответствующую кнопку
        const action = getActionFromHash();
        if (action && STATUS_TYPES.includes(action)) {
            const activeButton = document.querySelector(`[data-option="${action}"]`);
            if (activeButton) {
                activeButton.classList.add('active');
            }
        }
    }

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
      div.dataset.id = item;
    } else if (item.similar_article) {
      div.innerHTML = `
        <span class="article-text">${item.similar_article}</span>
        <span class="article-id">ID: ${item.id}</span>
      `;
      div.dataset.id = item.id;
    } else {
      div.innerHTML = `
        <span class="article-text">Артикул</span>
        <span class="article-id">ID: ${item.id}</span>
      `;
      div.dataset.id = item.id;
    }

    div.addEventListener('click', () => {
      // Устанавливаем ID товара в поле smart для ModelChoiceField
      input.value = div.dataset.id;
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



// Кастомная валидация для полей, Regex береться из формочки Django и подставляеться тут
document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('input[data-pattern]');

    inputs.forEach(input => {
        const fullPattern = input.dataset.pattern;  // например, '^[0-9]{12}$'

        // Извлечь длину из {N}
        const lengthMatch = fullPattern.match(/\{(\d+)\}/);
        const maxLength = lengthMatch ? parseInt(lengthMatch[1], 10) : 1000;

        // Извлечь допустимый набор символов из паттерна (пример для [0-9])
        // Ищем [..] внутри паттерна
        const charClassMatch = fullPattern.match(/\[([^\]]+)\]/);
        // Если нашли, берем содержимое, иначе пустая строка
        const allowedChars = charClassMatch ? charClassMatch[1] : '';

        // Создаем регулярку для одного символа на основе allowedChars
        const allowedCharPattern = new RegExp('[' + allowedChars + ']');

        input.addEventListener('input', function () {
            let clean = '';
            for (let i = 0; i < this.value.length; i++) {
                if (allowedCharPattern.test(this.value[i])) {
                    clean += this.value[i];
                }
                if (clean.length >= maxLength) break;
            }
            if (this.value !== clean) {
                this.value = clean;
            }
        });
    });
});





// Кастомная валидация для полей, Regex береться из формочки Django и подставляеться тут
document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('input[data-pattern]');

    inputs.forEach(input => {
        const fullPattern = input.dataset.pattern;  // например, '^[0-9]{12}$'

        // Извлечь длину из {N}
        const lengthMatch = fullPattern.match(/\{(\d+)\}/);
        const maxLength = lengthMatch ? parseInt(lengthMatch[1], 10) : 1000;

        // Извлечь допустимый набор символов из паттерна (пример для [0-9])
        // Ищем [..] внутри паттерна
        const charClassMatch = fullPattern.match(/\[([^\]]+)\]/);
        // Если нашли, берем содержимое, иначе пустая строка
        const allowedChars = charClassMatch ? charClassMatch[1] : '';

        // Создаем регулярку для одного символа на основе allowedChars
        const allowedCharPattern = new RegExp('[' + allowedChars + ']');

        input.addEventListener('input', function () {
            let clean = '';
            for (let i = 0; i < this.value.length; i++) {
                if (allowedCharPattern.test(this.value[i])) {
                    clean += this.value[i];
                }
                if (clean.length >= maxLength) break;
            }
            if (this.value !== clean) {
                this.value = clean;
            }
        });
    });
});

// -------- Sync comments between tabs (massage, offer)
document.addEventListener('DOMContentLoaded', function() {
    const mainComments = document.querySelector('#purchase-ebay-form textarea[name="comments"]');
    const mirrorIds = ['comments-mirror-massage', 'comments-mirror-offer'];
    const mirrors = mirrorIds.map(id => document.getElementById(id)).filter(Boolean);

    if (!mainComments || mirrors.length === 0) return;

    // Initialize mirrors with current value
    mirrors.forEach(m => {
        m.value = mainComments.value || '';
        const container = m.closest('.floating-label-container');
        if (container) {
            if (m.value && m.value !== '') container.classList.add('has-value');
            else container.classList.remove('has-value');
        }
    });

    // Update mirrors when main changes
    mainComments.addEventListener('input', function() {
        mirrors.forEach(m => {
            if (m.value !== mainComments.value) {
                m.value = mainComments.value;
                const container = m.closest('.floating-label-container');
                if (container) {
                    if (m.value && m.value !== '') container.classList.add('has-value');
                    else container.classList.remove('has-value');
                }
            }
        });
    });

    // Update main (and other mirrors) when any mirror changes
    mirrors.forEach(m => {
        m.addEventListener('input', function() {
            if (mainComments.value !== m.value) {
                mainComments.value = m.value;
                const evt = new Event('input', { bubbles: true });
                mainComments.dispatchEvent(evt);
            }
            // Propagate to other mirrors
            mirrors.forEach(other => {
                if (other !== m && other.value !== m.value) {
                    other.value = m.value;
                    const container = other.closest('.floating-label-container');
                    if (container) {
                        if (other.value && other.value !== '') container.classList.add('has-value');
                        else container.classList.remove('has-value');
                    }
                }
            });
        });
    });
});

// -------- Clear form button
document.addEventListener('DOMContentLoaded', function() {
    const clearBtn = document.getElementById('clear-form-btn');
    const form = document.getElementById('purchase-ebay-form');
    if (!clearBtn || !form) return;

    clearBtn.addEventListener('click', function() {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(el => {
            const name = el.getAttribute('name');
            // Сохраняем csrfmiddlewaretoken и status
            if (name === 'csrfmiddlewaretoken' || name === 'status') return;

            if (el.tagName === 'SELECT') {
                el.selectedIndex = -1;
            } else if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } else {
                el.value = '';
            }

            // Обновляем состояния плавающих лейблов
            const container = el.closest('.floating-label-container');
            if (container) {
                container.classList.remove('has-value');
                container.classList.remove('focused');
            }
        });

        // Очистить список автодополнения
        const list = document.getElementById('autoArticleComplete-list');
        if (list) {
            list.innerHTML = '';
            list.style.display = 'none';
            list.style.visibility = 'hidden';
        }

        // Сбросить статус на "Куплено" и переключить на соответствующую вкладку
        switchFormStatus('form-buy', false);
    });
});





