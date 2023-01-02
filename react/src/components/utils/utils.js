function addZero(i) {
  let res = i;
  if (i < 10) {
    res = `0${i}`;
  }
  return res;
}

// This file aimed to contain several functions
// eslint-disable-next-line import/prefer-default-export
export { addZero };
