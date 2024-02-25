package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

type price struct {
	Price string `json:"price"`
}

func index(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("got / request\n")
	io.WriteString(w, btcprice.Price)
}

func getbtc() {
	// Call binance API
	// https://dev.to/devkiran/make-an-http-get-request-in-go-58gf
	resp, err := http.Get("https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT")
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	jsonerr := json.NewDecoder(resp.Body).Decode(&btcprice)
	if jsonerr != nil {
		fmt.Println(jsonerr)
		return
	}
	fmt.Println(btcprice.Price)

}

func tickfunc() {
	ticker := time.NewTicker(60 * time.Second) // Tick every minute
	i := 0
	// https://www.golinuxcloud.com/golang-ticker/
	for range ticker.C {
		i++
		fmt.Println("tick ", i)
		getbtc()
	}
}

var btcprice price // Global BTC Price var

func main() {
	fmt.Println("Starting main")

	getbtc() //hack to populate the price before the cron loop

	// tick in background
	go tickfunc()

	http.HandleFunc("/", index)
	if err := http.ListenAndServe(":8888", nil); err != nil {
		fmt.Fprintf(os.Stderr, "error listening and serving: %s\n", err)
	}

}
