function currencyConverter(value, d){
    const options = {style: "currency",
                     currency:"EUR",
                     maximumFractionDigits: d, 
                     minimumFractionDigits: d};
    const formatter = new Intl.NumberFormat("en-US", options);
    return formatter.format(value);
}

function convertCurrency(value){
    return Number(value.replace(/[^0-9.-]+/g,""));
}

function niceNumber(value, decimals){
    const options = {maximumFractionDigits: decimals, 
                     minimumFractionDigits: decimals};
    const formatter = new Intl.NumberFormat(options);
    return formatter.format(value);
}