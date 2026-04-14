// loads header and footer into html files

async function loadComponent(id, file) {
  const res = await fetch(file);
  const html = await res.text();
  document.getElementById(id).innerHTML = html;
}
async function initComponents() {
  await loadComponent('header-placeholder', '/static/header.html');
  await loadComponent('footer-placeholder', '/static/footer.html');
  await loadComponent('modal-placeholder', '/static/sub-box.html');
}

initComponents();

// side panel for account button
function openPanel() {
    document.getElementById('accountPanel').classList.add('open');
    document.getElementById('overlay').classList.add('open');
}

function closePanel() {
    document.getElementById('accountPanel').classList.remove('open');
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('accountBtn').focus();
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closePanel();
});

// subscription functions 
  let currentProduct = { name: '', price: '' , current_id: 0};
  let qty = 1;
 
  const freqLabels = {
    daily:    'daily',
    weekly:   'weekly',
    biweekly: 'every 2 weeks',
    monthly:  'monthly',
    '3months':'evey 3 months',
    '6months':'every 6 months',
    yearly:   'yearly'
  };
 
  function openSubModal(name, price, product_id) {
    currentProduct = { name, price, product_id };
    qty = 1;
 
    document.getElementById('modalProductName').textContent = name;
    document.getElementById('modalProductPrice').textContent = price + ' per unit';
    document.getElementById('qtyDisplay').textContent = qty;
 
    // Reset to weekly by default
    document.getElementById('frequencySelect').value = 'weekly';
    updateSummary();
 
    document.getElementById('subModal').classList.add('open');
    document.addEventListener('keydown', handleSubEsc);
  }
 
  function closeSubModal() {
    document.getElementById('subModal').classList.remove('open');
    document.removeEventListener('keydown', handleSubEsc);
  }
 
  function handleSubEsc(e) {
    if (e.key === 'Escape') closeSubModal();
  }
 
  function changeQty(delta) {
    qty = Math.max(1, qty + delta);
    document.getElementById('qtyDisplay').textContent = qty;
    updateSummary();
  }
 
  function updateSummary() {
    const select = document.getElementById('frequencySelect');
    const freqText = freqLabels[select.value] || 'weekly';
 
    document.getElementById('summaryQty').textContent = qty;
    document.getElementById('summaryName').textContent = currentProduct.name || 'this item';
    document.getElementById('summaryFreq').textContent = freqText;
  }
 
  document.addEventListener('change', function(e) {
    if (e.target.id === 'frequencySelect') updateSummary();
  });
 
  async function confirmSubscription() {
    const select = document.getElementById('frequencySelect');
    const freq = select.value;

    const payload = {
        product_id: currentProduct.product_id,
        occurence: freq,
        qty: qty
    };

    try {
        
        const apiKey = getSecret(); 

        
        const response = await fetch('/api/v1/subscriptions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.status === 'success') {
            alert(`Success! Subscribed to ${currentProduct.name}.`);
            closeSubModal();
        } else {
            console.error("Server Error:", result.error.message);
            alert("Failed to subscribe: " + result.error.message);
        }

    } catch (err) {
        console.error("Network Error:", err);
        alert("Could not connect to the server.");
    }
}