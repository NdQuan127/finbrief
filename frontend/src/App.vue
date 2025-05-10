<template>
  <div id="app">
    <header>
      <h1>10-K Financial Analysis</h1>
    </header>
    <main>
      <router-view />
    </main>
    <footer>
      <p>© {{ new Date().getFullYear() }} 10-K Financial Analysis Tool</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Arial', 'Helvetica Neue', Helvetica, sans-serif;
  line-height: 1.6;
  color: #000000;
  background-color: #FFFDE7;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: #000000;
  color: #FFFF00;
  padding: 1rem;
  text-align: center;
  border-bottom: 3px solid #000000;
}

header h1 {
  font-size: 1.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

main {
  flex: 1;
  padding: 1.5rem;
  max-width: 900px;
  margin: 1.5rem auto;
  width: 90%;
  background-color: #FFFFFF;
  border: 3px solid #000000;
  box-shadow: 8px 8px 0px #000000;
}

footer {
  background-color: #000000;
  color: #FFFFFF;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
  border-top: 3px solid #000000;
}

.btn {
  display: inline-block;
  background: #FFFF00;
  color: #000000;
  border: 3px solid #000000;
  padding: 0.75rem 1.5rem;
  margin: 0.5rem 0;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 0;
  cursor: pointer;
  box-shadow: 4px 4px 0px #000000;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
  text-transform: uppercase;
}

.btn:hover {
  background: #F1C40F;
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #000000;
}

.btn:active {
  transform: translate(4px, 4px);
  box-shadow: none;
}

.btn:disabled {
  background: #BDC3C7;
  color: #7F8C8D;
  box-shadow: none;
  border-color: #7F8C8D;
  cursor: not-allowed;
}

.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  border-top-color: #000000;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.card {
  background: #FFFFFF;
  border: 3px solid #000000;
  box-shadow: 6px 6px 0px #000000;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: 0;
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1.25rem;
  color: #000000;
  text-transform: uppercase;
  border-bottom: 2px solid #000000;
  padding-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  font-size: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border: 2px solid #000000;
  border-radius: 0;
  background-color: #FFFFFF;
}

.form-control:focus {
  outline: 2px solid #0000FF;
  border-color: #0000FF;
}

input[type="radio"], input[type="checkbox"] {
  margin-right: 0.5rem;
  transform: scale(1.2);
  accent-color: #000000;
}

.alert {
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 0;
  border-width: 3px;
  border-style: solid;
  font-weight: bold;
}

.alert-danger {
  background-color: #FFCDD2;
  color: #B71C1C;
  border-color: #B71C1C;
}

.alert-success {
  background-color: #C8E6C9;
  color: #1B5E20;
  border-color: #1B5E20;
}

.alert-warning {
  background-color: #FFF9C4;
  color: #F57F17;
  border-color: #F57F17;
}

.text-success {
  color: #1B5E20;
}

.text-warning {
  color: #F57F17;
}

.text-danger {
  color: #B71C1C;
}
</style>
