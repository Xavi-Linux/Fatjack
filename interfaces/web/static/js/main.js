document.addEventListener("DOMContentLoaded",function(e){
    //Reset File functions
    document.forms["agent_picker"].reset();

    //Reset File functions - END
    //Common functions
    
    function removeChildren(node){
        while (node.firstChild){
            node.removeChild(node.firstChild);
        }
    }

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

    function toggleClass(element, clas, time){
        function addClass(element, clas){
            element.classList.add(clas);
        }
        function removeClass(element, clas){
            element.classList.remove(clas);
        }
        addClass(element, clas);
        setTimeout(function(){removeClass(element, clas)}, time);
    }

    

    function fillHand(element, array){
        const imgpath = "../static/img/cards/PNG/";
        array.forEach(function(item){
            var card = document.createElement("li");
            var img_card =(function(){var el = document.createElement("img");
                                   el.setAttribute("src", imgpath + item + ".png");
                                   el.setAttribute("alt", item);
                                   el.setAttribute("class", "card-img"); return el})();
            
            card.appendChild(img_card)
            element.appendChild(card);
        });
    }
    //END- Common functions
    //AJAX Functions
    function sendInfo(method, url, async, data, callback){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            if (request.readyState == 4){
                if (request.status == 200){
                    callback(request.responseText);
                }
            }
        }

        request.open(method, url, async);
        request.send(data);
    }

    function BuildForm(obj){
        var data = new FormData();
        const ks = Object.keys(obj);
        ks.forEach((key, index)=>{data.append(key, obj[key]);});
        return data;
    }

    //Ajax Functions - END
    //Events
    document.getElementById("stop").disabled = true;
    document.getElementById("play").disabled = true;

    function notice(){
        var picker =  document.getElementById("agents");
        if (picker.value == ""){
            toggleClass(picker, "red_light", 1000);
        }        
    }    
    setInterval(function(){notice()}, 2000);

    document.getElementById("agents").addEventListener("change", function(e){
        if (this.value != ""){
            var play = document.getElementById("play");
            play.disabled = false;
            play.classList.remove("disabled");
            play.classList.add("enabled");
        }
    });

    document.getElementById("agent_picker").addEventListener("submit", function(e){
        var picker =  document.getElementById("agents");
        if (picker.value != ""){
            var play = document.getElementById("play");
            play.disabled = true;
            play.classList.remove("enabled");
            play.classList.add("disabled");

            var stop = document.getElementById("stop");
            stop.disabled = false;
            stop.classList.remove("disabled");
            stop.classList.add("enabled");

            picker.setAttribute("disabled", "disabled");

            document.querySelector(".invisible").classList.remove("invisible");
            
            sendInfo("POST", "/start", true, BuildForm({agent: picker.value}), (text)=>{
                playBlackjack();
            });

            sendInfo("POST", "/results", true, BuildForm({agent: picker.value}), (text)=>{
                var obj = JSON.parse(text);
                var data = transformData(obj);
                lineChart("rewards", data);
                window.addEventListener("resize",function(e){
                    removeChildren(document.getElementById("rewards"));
                    lineChart("rewards", data);
                });
               
            });
                                         
            }

        e.preventDefault();
    });

    document.getElementById("stop").addEventListener("click", function(e){
            location.reload();
    });

    document.querySelector("#rules ul").addEventListener("mouseover", function(e){
        var rules = document.querySelector(".modal");
        if (!rules.classList.contains("animated-modal")){
            rules.classList.remove("unanimated-modal");
            rules.classList.add("animated-modal");            
        }


    });

    
    document.querySelector(".modal").addEventListener("mouseout", function(e){
        var rules = document.querySelector(".modal");
        rules.classList.add("unanimated-modal");
        setTimeout(function(){rules.classList.remove("animated-modal");}, 500);

    } );
   
    function playBlackjack(){

        sendInfo("GET", "/play", true, null, async (text)=>{
             var hands = JSON.parse(text)['hands'];
             while (hands.length > 0) {
                var hand = hands.shift();
                await handleHand(hand);};
            playBlackjack();
                    
        });


    }

    const delay = ms => new Promise(res => setTimeout(res, ms));
    const wait = 2000;
    const current_bet = 4;

    async function handleHand(hand){ 
        var message = document.getElementById("message");
        message.innerHTML = "Bet: €4";     
        setTimeout(function(){message.innerHTML="";}, wait)
        for (step in hand){
            await handleStep(hand[step]);
        };
        return warning = Promise.resolve("END of HAND");
    }

    async function handleStep(step){
        var dealer = document.querySelector("#dealer_cards .cards");
        var player = document.querySelector("#player_cards .cards");
        var action = step["action"];
        var terminal = step["terminal"];
        if (action != "-"){
            if (action == "0"){
                var button = document.getElementById("stand");
            }else{
                var button = document.getElementById("hit");              
            }
            toggleClass(button, "selection-colour", wait);
        }
        
        await delay(wait);
        removeChildren(dealer);
        removeChildren(player);
        document.querySelector("#dealer_value .score").innerHTML = step["points"][1];
        fillHand(dealer, step["cards"][1]);
        document.querySelector("#player_value .score").innerHTML = step['points'][0];
        fillHand(player, step["cards"][0]);
        if (terminal){
            await delay(wait);
            var reward = Number(step["reward"]);
            var message = document.getElementById("message");
            if (reward == 0){
                message.innerHTML = "Draw!";
            } else if(reward == 1){
                message.innerHTML = "Win!";
            } else if(reward == -1){
                message.innerHTML = "Loss!";
            } else if (reward == 1.5){
                message.innerHTML= "Blackjack!"
            }

            setTimeout(function(){message.innerHTML="";}, wait);
            moneyManager(reward, current_bet);
            await delay(wait);
            document.querySelector("#dealer_value .score").innerHTML = 0;
            document.querySelector("#player_value .score").innerHTML = 0;
            removeChildren(dealer);
            removeChildren(player);
        }
        await delay(wait);
    }

    function moneyManager(reward, bet){
        var gains = document.getElementById("gains");
        var total = document.getElementById("total");
        var amount = reward * bet;
        
        var func = (element, money) => {element.innerHTML = currencyConverter(convertCurrency(element.innerHTML) + money, 0);};
        func(gains, amount);
        func(total, amount);

    };


    //Events - END
});