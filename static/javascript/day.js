
const button = document.getElementById('submit_btn');
function onload_func()
{
    document.getElementById("plot").style.display = "none";
}


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
   document.getElementById("plot").style.display = "block";
});

