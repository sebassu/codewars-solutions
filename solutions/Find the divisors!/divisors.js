function divisors(integer) {
  const result = [];
  for (let i = 2; i <= Math.sqrt(integer); i++) {
    if (integer % i === 0) {
      result.push(i);
      const factor = integer / i;
      if (i !== factor) {
        result.push(factor);
      }
    }
  }
  return result.length ? result.sort((a, b) => a - b) : `${integer} is prime`;
}
