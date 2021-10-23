
const button = document.getElementById('submit_btn');

button.addEventListener('click', async _ => {
  try {
    const response = await fetch('/selectDate', {
      method: 'post',
      body: {
        let startDate =  document.getElementById('submit_btn');
      }
    });
    console.log('Completed!', response);
  } catch(err) {
    console.error(`Error: ${err}`);
  }
});
