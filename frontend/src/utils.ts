export const formatCompactNumber = (number: number): string => {
  if (number === undefined || number === null) return "0";
  
  if (number < 1000) {
    return new Intl.NumberFormat('en-US').format(number);
  }

  return new Intl.NumberFormat('en-US', {
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 2
  }).format(number);
};
