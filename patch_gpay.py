"""Apply: (1) transparent live-camera QR scanner, (2) Google Pay payment button,
(3) sample store catalogue from google-pay/react-store.

Every replacement is asserted so a missed match fails loudly instead of silently
skinning the patch.
"""
import io, sys

P = 'src/main/assets/gpay.html'
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, count=1):
    global s
    if old not in s:
        sys.exit('PATTERN NOT FOUND:\n' + old[:400])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- 1. CSS ----
sub(
"""  /* ============ SCANNER ============ */
  .scan-topbar{display:flex; align-items:center; gap:2px; padding:4px 6px; background:rgba(0,0,0,.6);}""",
"""  /* ============ SCANNER ============ */
  .scan-screen{position:relative; overflow:hidden;}
  .cam-video{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; background:#000; z-index:0;}
  .scan-topbar{display:flex; align-items:center; gap:2px; padding:4px 6px; background:rgba(0,0,0,.6);
    position:relative; z-index:4;}""")

sub(
"""  .viewfinder{position:relative; margin:8px 16px 0; flex:1; min-height:190px; border-radius:20px; overflow:hidden;
    background:#0a0d0c; cursor:pointer;}""",
"""  /* the viewfinder is a lit window onto the live camera: the huge spread shadow
     dims everything outside it, so the feed reads through the rounded corners */
  .viewfinder{position:relative; z-index:2; margin:8px 16px 0; flex:1; min-height:190px; border-radius:20px;
    overflow:hidden; background:#0a0d0c; cursor:pointer; box-shadow:0 0 0 100vmax rgba(0,0,0,.62);}
  .scan-screen.live .viewfinder{background:transparent;}
  .scan-screen.live .cam-feed{display:none;}
  .cam-badge{position:absolute; top:10px; left:10px; z-index:5; display:none; align-items:center; gap:6px;
    background:rgba(0,0,0,.55); color:#fff; font-size:10.5px; letter-spacing:.4px; text-transform:uppercase;
    border-radius:20px; padding:4px 10px;}
  .scan-screen.live .cam-badge{display:flex;}
  .cam-badge i{width:7px; height:7px; border-radius:50%; background:#f28b82; display:block;}""")

sub(
"""  .upload-btn{align-self:center; display:flex; align-items:center; gap:8px; background:#fff; color:#000; border:0;
    border-radius:24px; padding:10px 18px; font-family:inherit; font-size:13.5px; font-weight:600; cursor:pointer; margin:14px 0 4px;}""",
"""  .upload-btn{align-self:center; display:flex; align-items:center; gap:8px; background:#fff; color:#000; border:0;
    border-radius:24px; padding:10px 18px; font-family:inherit; font-size:13.5px; font-weight:600; cursor:pointer;
    margin:14px 0 4px; position:relative; z-index:4;}""")

sub(
"""  .scan-sheet{background:var(--surface); border-radius:20px 20px 0 0; padding:10px 20px 26px; margin-top:auto; text-align:center;}""",
"""  .scan-sheet{background:var(--surface); border-radius:20px 20px 0 0; padding:10px 20px 26px; margin-top:auto;
    text-align:center; position:relative; z-index:4;}""")

# Google Pay button + sample store styles, appended next to the button styles
sub(
"""  /* ============ SUCCESS ============ */""",
"""  /* ============ GOOGLE PAY BUTTON ============ */
  .gpay-wrap{margin-bottom:10px; display:none;}
  .gpay-btn{width:100%; display:flex; align-items:center; justify-content:center; gap:6px; background:#000; color:#fff;
    border:0; border-radius:8px; padding:13px 16px; font-family:inherit; font-size:15px; cursor:pointer;}
  .gpay-btn:active{opacity:.85;}
  .gpay-btn[disabled]{background:#1a1a1a; color:#6a6a6a; cursor:default;}
  .gpay-lead{font-size:13px; font-weight:500; opacity:.92;}
  .gpay-mark{display:flex; align-items:center; gap:2px; font-size:17px; font-weight:600; letter-spacing:-.2px;}
  .gpay-mark .glogo{width:20px; height:20px; flex:none;}
  .gpay-note{font-size:11px; color:var(--text-3); text-align:center; margin:8px 0 0; line-height:1.45;}
  .shop-item{display:flex; align-items:center; gap:12px; background:var(--surface); border-radius:12px; padding:11px 12px;
    margin-bottom:8px; cursor:pointer;}
  .shop-item:active{background:var(--surface-2);}
  .shop-item .thumb{width:44px; height:44px; border-radius:10px; flex:none; display:flex; align-items:center; justify-content:center;
    font-size:20px; background:#2a2a2a;}
  .shop-item b{display:block; font-size:13.5px; font-weight:500; line-height:1.3;}
  .shop-item em{font-style:normal; font-size:11.5px; color:var(--text-3);}
  .shop-item .price{margin-left:auto; font-size:14px; font-weight:500; white-space:nowrap;}

  /* ============ SUCCESS ============ */""")

# ---------------------------------------------------------------- 2. HTML ---
# 2a. scanner: live camera video + badge
sub(
"""  <section class="screen" id="s-scan">
    <div class="scan-topbar">""",
"""  <section class="screen scan-screen" id="s-scan">
    <video class="cam-video" id="camVideo" autoplay playsinline muted></video>
    <div class="cam-badge"><i></i>Live camera</div>
    <div class="scan-topbar">""")

# 2b. amount screen: Google Pay button above the sandbox Pay button
sub(
"""    <div class="paybar"><button class="btn" id="payBtn" onclick="startPay()" disabled>Pay</button></div>""",
"""    <div class="paybar">
      <div class="gpay-wrap" id="gpayWrap">
        <button class="gpay-btn" id="gpayBtn" onclick="gpayCheckout()">
          <span class="gpay-lead">Pay with</span>
          <span class="gpay-mark">
            <svg class="glogo" viewBox="0 0 48 48" aria-hidden="true">
              <path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/>
              <path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/>
              <path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/>
              <path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2 15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/>
            </svg>Pay
          </span>
        </button>
        <p class="gpay-note" id="gpayNote">Google Pay button &middot; sandbox</p>
      </div>
      <button class="btn" id="payBtn" onclick="startPay()" disabled>Pay</button>
    </div>""")

# 2c. sample store sheet
sub(
"""  <div class="sheet" id="upiLiteSheet">""",
"""  <div class="sheet" id="shopSheet">
    <h3>Sample store</h3>
    <p>Demo catalogue from google-pay/react-store &mdash; the Google Pay sample store. Prices are the sample USD
       values converted to &#8377; for this sandbox.</p>
    <div id="shopList"></div>
    <div style="margin-top:18px;"><button class="btn ghost" onclick="closeSheet()">Close</button></div>
  </div>
  <div class="sheet" id="upiLiteSheet">""")

# ---------------------------------------------------------------- 3. JS ----
# 3a. sample catalogue + merchant flags
sub(
"""const RECHARGE_PLANS = [10, 20, 50, 100, 200, 500];""",
"""const RECHARGE_PLANS = [10, 20, 50, 100, 200, 500];
/* Demo catalogue copied from google-pay/react-store (public/data/mens_tshirts.json).
   usd = the sample store's own price, inr = the same price converted for the UPI sandbox. */
const USD_TO_INR = 83;
const SAMPLE_ITEMS = [
  {title:'YouTube Organic Cotton T-Shirt - Grey',  usd:14.75, vpa:'reactstore@ybl',     color:'#5f6368', emoji:'\U0001F455'},
  {title:'Inbox - Subtle Actions T-Shirt',        usd:17.05, vpa:'reactstore@ybl',     color:'#1a73e8', emoji:'\U0001F455'},
  {title:'Adult Android Superhero T-Shirt',       usd:14.95, vpa:'reactstore@ybl',     color:'#3ddc84', emoji:'\U0001F455'},
  {title:"Men's Vintage Heather T-Shirt",         usd:15.80, vpa:'reactstore@ybl',     color:'#7d7360', emoji:'\U0001F455'},
  {title:'Basic Black T-Shirt',                   usd:16.90, vpa:'reactstore@ybl',     color:'#202124', emoji:'\U0001F455'},
  {title:'Go Gopher T-Shirt in Teal',             usd:10.95, vpa:'reactstore@ybl',     color:'#00acc1', emoji:'\U0001F455'},
].map(it => Object.assign(it, { inr: Math.round(it.usd * USD_TO_INR) }));""")

sub(
"""const MERCHANTS = [
  {name:'Third Wave Coffee', vpa:'thirdwaveco@axisbank', color:'#b06f00', emoji:'☕', tag:'Coffee shop'},
  {name:"Domino's Pizza",    vpa:'dominos@icici',        color:'#d93025', emoji:'🍕', tag:'Food & drinks'},
  {name:'Chaayos',           vpa:'chaayos@paytm',        color:'#0f9d58', emoji:'🍵', tag:'Restaurant'},
  {name:'Zomato',            vpa:'zomato@ybl',           color:'#e8710a', emoji:'🛵', tag:'Food delivery'},
];""",
"""const MERCHANTS = [
  {name:'Third Wave Coffee', vpa:'thirdwaveco@axisbank', color:'#b06f00', emoji:'☕', tag:'Coffee shop', merchant:true},
  {name:"Domino's Pizza",    vpa:'dominos@icici',        color:'#d93025', emoji:'🍕', tag:'Food & drinks', merchant:true},
  {name:'Chaayos',           vpa:'chaayos@paytm',        color:'#0f9d58', emoji:'🍵', tag:'Restaurant', merchant:true},
  {name:'Zomato',            vpa:'zomato@ybl',           color:'#e8710a', emoji:'🛵', tag:'Food delivery', merchant:true},
];""")

# 3b. sample store entry on the home business grid
sub(
"""  document.getElementById('bizGrid').innerHTML = MERCHANTS.map(m =>
    `<div class="biz-card" onclick="startAmount({name:'${esc(m.name)}',vpa:'${m.vpa}',color:'${m.color}',emoji:'${m.emoji}'})">
      <div class="logo" style="background:${m.color}22">${m.emoji}</div>
      <div><b>${m.name}</b><em>${m.tag}</em></div></div>`).join('');""",
"""  document.getElementById('bizGrid').innerHTML = MERCHANTS.map(m =>
    `<div class="biz-card" onclick="startAmount({name:'${esc(m.name)}',vpa:'${m.vpa}',color:'${m.color}',emoji:'${m.emoji}',merchant:true})">
      <div class="logo" style="background:${m.color}22">${m.emoji}</div>
      <div><b>${m.name}</b><em>${m.tag}</em></div></div>`).join('')
    + `<div class="biz-card" onclick="openShop()">
      <div class="logo" style="background:#1a73e822">\U0001F6D2</div>
      <div><b>Sample store</b><em>Google Pay checkout</em></div></div>`;""")

# 3c. shop sheet rendering + Google Pay for Web integration
sub(
"""/* ===================== SCAN FLOW ===================== */""",
"""/* ===================== SAMPLE STORE ===================== */
function openShop(){
  document.getElementById('shopList').innerHTML = SAMPLE_ITEMS.map(it=>
    `<div class="shop-item" onclick="closeSheet(); startAmount({name:'${esc(it.title)}',vpa:'${it.vpa}',color:'${it.color}',emoji:'${it.emoji}',amount:${it.inr},merchant:true,note:'${esc(it.title)}'})">
      <div class="thumb">${it.emoji}</div>
      <div style="min-width:0;"><b>${it.title}</b><em>$${it.usd.toFixed(2)} &middot; &#8377;${it.inr.toLocaleString('en-IN')}</em></div>
      <div class="price">&#8377;${it.inr.toLocaleString('en-IN')}</div></div>`).join('');
  openSheet('shopSheet');
}

/* ===================== GOOGLE PAY (for Web) =====================
   Mirrors google-pay/online-quickstart-web + google-pay/gpay-live-demo:
   a paymentRequest with a google_pay method and a CARD gateway method.
   When the real API is unreachable (offline / no merchant) the button falls
   back to the sandbox UPI-PIN flow.                                     */
const GPAY_SCRIPT = 'https://pay.google.com/gp/p/js/pay.js';
let gpayClient = null;
let gpaySupported = false;
let gpayChecked = false;

function buildPaymentRequest(amount, label){
  return {
    apiVersion: 2,
    apiVersionMinor: 0,
    allowedPaymentMethods: [
      {
        type: 'google_pay',
        parameters: {
          environment: 'TEST',
          apiVersion: 2,
          apiVersionMinor: 0,
          allowedPaymentMethods: ['CARD'],
          allowedCardNetworks: ['AMEX','DISCOVER','JCB','MASTERCARD','VISA'],
        },
      },
      {
        type: 'CARD',
        parameters: {
          allowedAuthMethods: ['PAN_ONLY','CRYPTOGRAM_3DS'],
          allowedCardNetworks: ['AMEX','DISCOVER','JCB','MASTERCARD','VISA'],
          billingAddressParameters: { format: 'MIN' },
        },
        tokenizationSpecification: {
          type: 'PAYMENT_GATEWAY',
          parameters: { gateway: 'example', gatewayMerchantId: 'exampleGatewayMerchantId' },
        },
      },
    ],
    merchantInfo: { merchantName: 'Google Pay Sample Store' },
    transactionInfo: {
      totalPriceStatus: 'FINAL',
      totalPriceLabel: label || 'Total',
      totalPrice: Number(amount).toFixed(2),
      currencyCode: 'INR',
      countryCode: 'IN',
    },
  };
}
function loadGooglePay(){
  if (gpayChecked || document.getElementById('gpay-script')) return;
  gpayChecked = true;
  const sc = document.createElement('script');
  sc.id = 'gpay-script';
  sc.async = true;
  sc.src = GPAY_SCRIPT;
  sc.onload = onGooglePayLoaded;
  sc.onerror = () => setGpayNote('Google Pay API unavailable &middot; using the sandbox UPI PIN');
  document.head.appendChild(sc);
}
function onGooglePayLoaded(){
  try {
    gpayClient = new google.payments.api.PaymentsClient({ environment: 'TEST' });
    gpayClient.isBrowserSupported().then(function (res) {
      gpaySupported = !!(res && res.result);
      setGpayNote(gpaySupported
        ? 'Google Pay for Web &middot; TEST environment, no real money moves'
        : 'Google Pay not available here &middot; falls back to the sandbox UPI PIN');
    }).catch(function () {
      gpaySupported = false;
      setGpayNote('Google Pay not available here &middot; falls back to the sandbox UPI PIN');
    });
  } catch (e) {
    gpaySupported = false;
  }
}
function setGpayNote(html){
  const el = document.getElementById('gpayNote');
  if (el) el.innerHTML = html;
}
function gpayCheckout(){
  const amount = Math.round(parseFloat(document.getElementById('amtInput').value || 0) * 100) / 100;
  if (!(amount > 0)) return;
  if (gpaySupported && gpayClient) {
    gpayClient.loadPaymentSheet(buildPaymentRequest(amount, currentPayee && currentPayee.name)).then(function (res) {
      if (res.status === 'Canceled') return;
      if (res.status === 'Error') {
        setGpayNote('Google Pay error &middot; falling back to the sandbox UPI PIN');
        openUpiPin(amount);
        return;
      }
      const pd = res.payload || {};
      setGpayNote('Payment token received from Google Pay (sandbox)');
      completeGpayPayment(amount, pd);
    }).catch(function () {
      openUpiPin(amount);
    });
  } else {
    openUpiPin(amount);
  }
}
function completeGpayPayment(amount, payload){
  const note = document.getElementById('noteInput').value.trim();
  const t = { sid: Date.now(), ts: Date.now(), dir: 'out', name: currentPayee.name,
    sub: currentPayee.vpa || ('+91 ' + currentPayee.num), amount,
    time: nowLabel(), tid: makeUTR(), status: 'Completed', note,
    source: 'google_pay',
    gateway: (payload && payload.paymentMethodData && payload.paymentMethodData.tokenizationData &&
              payload.paymentMethodData.tokenizationData.type) || 'sandbox' };
  history.unshift(t);
  saveHistory();
  renderRecent();
  stack = ['s-success'];
  show('s-success');
  fillSuccess(t);
}

/* ===================== SCAN FLOW ===================== */""")

# 3d. live camera
sub(
"""/* ===================== SCAN FLOW ===================== */
let scanTimer=null;""",
"""/* ===================== SCAN FLOW ===================== */
let scanTimer=null;
let camStream=null;

function startCamera(){
  const video = document.getElementById('camVideo');
  const screen = document.getElementById('s-scan');
  if (!video || !screen) return;
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
  if (camStream) return;
  navigator.mediaDevices.getUserMedia({
    video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } },
    audio: false
  }).then(function (stream) {
    camStream = stream;
    video.srcObject = stream;
    const p = video.play();
    if (p && p.catch) p.catch(function(){});
    screen.classList.add('live');
  }).catch(function () {
    camStream = null;
    screen.classList.remove('live');
  });
}
function stopCamera(){
  if (camStream){
    camStream.getTracks().forEach(function (t) { t.stop(); });
    camStream = null;
  }
  const video = document.getElementById('camVideo');
  if (video) video.srcObject = null;
  const screen = document.getElementById('s-scan');
  if (screen) screen.classList.remove('live');
}""")

# 3e. hook the camera + Google Pay loader into navigation
sub(
"""function show(id){
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.getElementById('app').classList.toggle('nav-on', id==='s-home' || id==='s-money' || id==='s-you');
  document.querySelectorAll('.bn-item').forEach(b => b.classList.toggle('on', b.dataset.tab===id));
}""",
"""function show(id){
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.getElementById('app').classList.toggle('nav-on', id==='s-home' || id==='s-money' || id==='s-you');
  document.querySelectorAll('.bn-item').forEach(b => b.classList.toggle('on', b.dataset.tab===id));
  if (id === 's-scan') startCamera(); else stopCamera();
}""")

# 3f. amount screen: show the Google Pay button for merchant checkouts
sub(
"""  const amt = document.getElementById('amtInput');
  amt.value = payee.amount ? String(payee.amount) : '';
  document.getElementById('noteInput').value = '';
  updatePayBtn();
  go('s-amount');""",
"""  const amt = document.getElementById('amtInput');
  amt.value = payee.amount ? String(payee.amount) : '';
  document.getElementById('noteInput').value = payee.note || '';
  const wrap = document.getElementById('gpayWrap');
  if (wrap) wrap.style.display = payee.merchant ? 'block' : 'none';
  if (payee.merchant) loadGooglePay();
  updatePayBtn();
  go('s-amount');""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched -> %d bytes' % len(s))
