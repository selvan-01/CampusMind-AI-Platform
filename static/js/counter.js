const counters = document.querySelectorAll(".counter");

counters.forEach((counter) => {
  const target = +counter.dataset.target;
  let count = 0;

  const update = () => {
    count += target / 50;
    if (count < target) {
      counter.innerText = Math.ceil(count);
      setTimeout(update, 30);
    } else {
      counter.innerText = target;
    }
  };

  update();
});
