document.documentElement.classList.add('js-ready');

document.addEventListener('DOMContentLoaded', function () {
    initHeaderScroll();
    initHeroSlider();
    initScrollReveal();
    initBackToTop();
    initMobileFilter();
    initMobileNav();
    initCartConfirm();
    initAjaxCartAdd();
    initProductModal();
});

function initHeaderScroll() {
    const header = document.getElementById('siteHeader');
    if (!header) return;

    const onScroll = () => {
        header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
}

function initHeroSlider() {
    const slider = document.querySelector('.hero-slider');
    if (!slider) return;

    const slides = slider.querySelectorAll('.hero-slide');
    const dots = slider.querySelectorAll('.hero-dot');
    const prevBtn = slider.querySelector('.hero-arrow--prev');
    const nextBtn = slider.querySelector('.hero-arrow--next');
    const progressBar = slider.querySelector('.hero-progress__bar');
    const AUTOPLAY_MS = 6000;
    let current = 0;
    let autoplayTimer;

    function restartProgress() {
        if (!progressBar) return;
        progressBar.style.animation = 'none';
        progressBar.offsetHeight;
        progressBar.style.animation = 'heroProgress ' + (AUTOPLAY_MS / 1000) + 's linear forwards';
    }

    function goTo(index) {
        current = (index + slides.length) % slides.length;
        slides.forEach((slide, i) => {
            const active = i === current;
            slide.classList.toggle('is-active', active);
            slide.hidden = !active;
        });
        dots.forEach((dot, i) => dot.classList.toggle('is-active', i === current));
        restartProgress();
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    function startAutoplay() {
        stopAutoplay();
        autoplayTimer = setInterval(next, AUTOPLAY_MS);
    }

    function stopAutoplay() {
        if (autoplayTimer) clearInterval(autoplayTimer);
    }

    dots.forEach((dot, i) => {
        dot.addEventListener('click', () => {
            goTo(i);
            startAutoplay();
        });
    });

    if (prevBtn) prevBtn.addEventListener('click', () => { prev(); startAutoplay(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { next(); startAutoplay(); });

    slider.addEventListener('mouseenter', stopAutoplay);
    slider.addEventListener('mouseleave', startAutoplay);

    let touchStartX = 0;
    slider.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    slider.addEventListener('touchend', (e) => {
        const diff = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(diff) > 50) {
            diff < 0 ? next() : prev();
            startAutoplay();
        }
    }, { passive: true });

    goTo(0);
    startAutoplay();
}

function initScrollReveal() {
    const elements = document.querySelectorAll('.reveal');
    if (!elements.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    elements.forEach((el) => {
        observer.observe(el);
        /* элементы уже в зоне видимости при загрузке */
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            el.classList.add('is-visible');
        }
    });
}

function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        btn.classList.toggle('is-visible', window.scrollY > 400);
    }, { passive: true });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

function initMobileNav() {
    const nav = document.getElementById('navbarMain');
    if (!nav) return;

    nav.querySelectorAll('.header-nav__link').forEach((link) => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992 && nav.classList.contains('show')) {
                const toggler = document.querySelector('.header-toggler');
                if (toggler && window.bootstrap) {
                    window.bootstrap.Collapse.getOrCreateInstance(nav).hide();
                }
            }
        });
    });
}

function initMobileFilter() {
    const toggle = document.getElementById('filterToggle');
    const panel = document.getElementById('filterPanel');
    if (!toggle || !panel) return;

    toggle.addEventListener('click', () => {
        panel.classList.toggle('is-open');
        const expanded = panel.classList.contains('is-open');
        toggle.setAttribute('aria-expanded', expanded);
    });
}

function initCartConfirm() {
    document.querySelectorAll('.delete-cart-item').forEach((form) => {
        form.addEventListener('submit', (e) => {
            if (!confirm('Удалить товар из корзины?')) e.preventDefault();
        });
    });

    const priceRange = document.getElementById('priceRange');
    const priceValue = document.getElementById('priceValue');
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', function () {
            priceValue.textContent = this.value;
        });
    }
}

function updateCartBadge(total) {
    const badge = document.getElementById('cartBadge');
    if (!badge) return;

    if (total > 0) {
        badge.textContent = total;
        badge.classList.remove('d-none');
    } else {
        badge.textContent = '0';
        badge.classList.add('d-none');
    }
}

function updateProductAvailability(productId, availableStock) {
    const stock = Math.max(0, parseInt(availableStock, 10) || 0);
    const id = String(productId);

    document.querySelectorAll('[data-product-id="' + id + '"]').forEach((card) => {
        card.dataset.productStock = stock;

        const stockLabel = card.querySelector('[data-stock-label]');
        if (stockLabel) {
            stockLabel.className = 'product-card__stock ' +
                (stock > 0 ? 'product-card__stock--in' : 'product-card__stock--out');
            stockLabel.innerHTML =
                '<span class="product-card__stock-dot"></span> ' +
                (stock > 0 ? 'в наличии · ' + stock + ' шт.' : 'под заказ');
        }

        const expressBadge = card.querySelector('[data-express-badge]');
        if (expressBadge) {
            expressBadge.classList.toggle('d-none', stock === 0);
        }

        const cartForm = card.querySelector('[data-cart-form]');
        const outBtn = card.querySelector('[data-out-of-stock-btn]');
        if (cartForm) cartForm.classList.toggle('d-none', stock === 0);
        if (outBtn) outBtn.classList.toggle('d-none', stock > 0);
    });

    const detailBadge = document.getElementById('productStockBadge');
    if (detailBadge && detailBadge.dataset.productId === id) {
        if (stock > 0) {
            detailBadge.className = 'stock-badge mb-3 stock-badge--in';
            detailBadge.innerHTML =
                '<i class="fas fa-check-circle"></i> В наличии · <span id="productStockCount">' +
                stock + '</span> шт.';
        } else {
            detailBadge.className = 'stock-badge mb-3 stock-badge--out';
            detailBadge.innerHTML = '<i class="fas fa-clock"></i> Нет в наличии';
        }

        const detailForm = document.getElementById('productCartForm');
        const detailOutBtn = document.getElementById('productOutOfStockBtn');
        const qtyInput = document.getElementById('quantity');
        if (detailForm) detailForm.classList.toggle('d-none', stock === 0);
        if (detailOutBtn) detailOutBtn.classList.toggle('d-none', stock > 0);
        if (qtyInput) {
            qtyInput.max = stock;
            if (parseInt(qtyInput.value, 10) > stock) {
                qtyInput.value = stock || 1;
            }
        }
    }

    const modal = document.getElementById('productModal');
    if (modal && modal.dataset.currentProductId === id) {
        const modalStock = document.getElementById('productModalStock');
        const modalQty = document.getElementById('productModalQty');
        const modalForm = document.getElementById('productModalForm');
        const modalSubmit = document.getElementById('productModalSubmit');
        const modalBadge = document.getElementById('productModalBadge');
        const modalSpecs = document.getElementById('productModalSpecs');

        if (stock > 0) {
            if (modalStock) {
                modalStock.textContent = 'В наличии · ' + stock + ' шт.';
                modalStock.className = 'product-modal__stock is-in';
            }
            if (modalQty) {
                modalQty.max = stock;
                if (parseInt(modalQty.value, 10) > stock) {
                    modalQty.value = stock;
                }
                modalQty.disabled = false;
            }
            if (modalForm) modalForm.hidden = false;
            if (modalSubmit) modalSubmit.disabled = false;
            if (modalBadge) modalBadge.hidden = false;
        } else {
            if (modalStock) {
                modalStock.textContent = 'Под заказ';
                modalStock.className = 'product-modal__stock is-out';
            }
            if (modalForm) modalForm.hidden = true;
            if (modalBadge) modalBadge.hidden = true;
        }

        if (modalSpecs) {
            const rows = modalSpecs.querySelectorAll('li');
            rows.forEach((row) => {
                const label = row.querySelector('span');
                if (label && label.textContent === 'Наличие') {
                    const strong = row.querySelector('strong');
                    if (strong) {
                        strong.textContent = stock > 0 ? stock + ' шт.' : 'Под заказ';
                    }
                }
            });
        }
    }
}

function showToast(message, type) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = 'alert alert-flora alert-dismissible fade show' +
        (type === 'success' ? ' alert-flora--success' : ' alert-flora--error');
    alert.setAttribute('role', 'alert');
    alert.innerHTML =
        '<i class="fas fa-' + (type === 'success' ? 'check-circle' : 'circle-exclamation') + ' me-2"></i>' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>';

    container.appendChild(alert);

    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 3500);
}

function initAjaxCartAdd() {
    document.querySelectorAll('.js-cart-add').forEach((form) => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = form.querySelector('[type="submit"]');
            const originalHtml = submitBtn ? submitBtn.innerHTML : '';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Добавляем…';
            }

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    updateCartBadge(data.cart_total_items);
                    if (data.product_id != null && data.available_stock != null) {
                        updateProductAvailability(data.product_id, data.available_stock);
                    }
                    showToast(data.message, 'success');

                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Добавлено';
                        setTimeout(() => {
                            submitBtn.innerHTML = originalHtml;
                            submitBtn.disabled = false;
                        }, 1600);
                    }
                } else {
                    if (data.product_id != null && data.available_stock != null) {
                        updateProductAvailability(data.product_id, data.available_stock);
                    }
                    showToast(data.message || 'Не удалось добавить товар', 'error');
                    if (submitBtn) {
                        submitBtn.innerHTML = originalHtml;
                        submitBtn.disabled = false;
                    }
                }
            } catch (err) {
                showToast('Не удалось добавить товар. Попробуйте ещё раз.', 'error');
                if (submitBtn) {
                    submitBtn.innerHTML = originalHtml;
                    submitBtn.disabled = false;
                }
            }
        });
    });
}

function initProductModal() {
    const modal = document.getElementById('productModal');
    if (!modal) return;

    const els = {
        image: document.getElementById('productModalImage'),
        placeholder: document.getElementById('productModalPlaceholder'),
        badge: document.getElementById('productModalBadge'),
        category: document.getElementById('productModalCategory'),
        title: document.getElementById('productModalTitle'),
        price: document.getElementById('productModalPrice'),
        stock: document.getElementById('productModalStock'),
        desc: document.getElementById('productModalDesc'),
        specs: document.getElementById('productModalSpecs'),
        form: document.getElementById('productModalForm'),
        qty: document.getElementById('productModalQty'),
        submit: document.getElementById('productModalSubmit'),
        link: document.getElementById('productModalLink'),
    };

    function formatPrice(value) {
        const num = parseFloat(value);
        if (Number.isNaN(num)) return value;
        return new Intl.NumberFormat('ru-RU').format(num) + ' ₽';
    }

    function openFromCard(card) {
        const name = card.dataset.productName || '';
        const price = card.dataset.productPrice || '';
        const description = card.dataset.productDescription || '';
        const category = card.dataset.productCategory || '';
        const stock = parseInt(card.dataset.productStock, 10) || 0;
        const imageUrl = card.dataset.productImage || '';
        const productUrl = card.dataset.productUrl || '#';
        const cartUrl = card.dataset.cartUrl || '';

        els.title.textContent = name;
        els.category.textContent = category;
        els.price.textContent = formatPrice(price);
        els.desc.textContent = description;

        if (imageUrl) {
            els.image.src = imageUrl;
            els.image.alt = name;
            els.image.hidden = false;
            els.placeholder.hidden = true;
        } else {
            els.image.hidden = true;
            els.placeholder.hidden = false;
        }

        if (stock > 0) {
            els.stock.textContent = 'В наличии · ' + stock + ' шт.';
            els.stock.className = 'product-modal__stock is-in';
            els.badge.textContent = 'Экспресс-доставка';
            els.badge.hidden = false;
            els.form.action = cartUrl;
            els.form.hidden = false;
            els.qty.value = 1;
            els.qty.max = stock;
            els.qty.disabled = false;
            els.submit.disabled = false;
        } else {
            els.stock.textContent = 'Под заказ';
            els.stock.className = 'product-modal__stock is-out';
            els.badge.hidden = true;
            els.form.hidden = true;
        }

        els.specs.innerHTML = '';
        const specs = [
            ['Категория', category],
            ['Наличие', stock > 0 ? stock + ' шт.' : 'Под заказ'],
            ['Состав', 'Свежие сезонные цветы'],
            ['Упаковка', 'Авторская флористическая'],
            ['Доставка', 'От 2 часов по городу'],
        ];
        specs.forEach(([label, value]) => {
            const li = document.createElement('li');
            li.innerHTML = '<span>' + label + '</span><strong>' + value + '</strong>';
            els.specs.appendChild(li);
        });

        els.link.href = productUrl;
        modal.dataset.currentProductId = card.dataset.productId || '';

        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
    }

    function closeModal() {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
    }

    document.querySelectorAll('[data-quick-view]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const card = btn.closest('[data-product-id]');
            if (card) openFromCard(card);
        });
    });

    modal.querySelectorAll('[data-modal-close]').forEach((el) => {
        el.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('is-open')) {
            closeModal();
        }
    });
}
