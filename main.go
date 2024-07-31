package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()

func main() {

	// Parse arguments and convert to Int
	args := os.Args
	fmt.Println(args[0], args[1], args[2], args[3])
	total_args := len(os.Args[1:])
	fmt.Println("Total Args =", total_args)

	pattern := args[1]

	db1, err := strconv.Atoi(args[2])
	if err != nil {
		log.Fatal("Missing source DB parameter:", err)
	}

	db2, err := strconv.Atoi(args[3])
	if err != nil {
		log.Fatal("Missing target DB parameter:", err)
	}

	// Connect to Redis = Client 1
	client1 := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // Replace with your Redis server address
		Password: "",               // No password for local development
		DB:       db1,              // DB 1
	})

	client1.FlushAll(ctx)

	// Connect to Redis = Client 2 - because I couldn't yet figure out how to reuse connection :(
	client2 := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // Replace with your Redis server address
		Password: "",               // No password for local development
		DB:       db2,              // DB 2
	})

	client1.FlushAll(ctx)
	// Ping the Redis server to check the connection #1
	pong1, err := client1.Ping(ctx).Result()

	if err != nil {
		log.Fatal("Error connecting to Redis Client 1:", err)
	}

	fmt.Println("Connected to Redis Client 1:", pong1)

	// Ping the Redis server to check the connection #1
	pong2, err := client2.Ping(ctx).Result()

	if err != nil {
		log.Fatal("Error connecting to Redis Client 2:", err)
	}

	fmt.Println("Connected to Redis Client 2:", pong2)

	//create and initialize the map of key/values
	my_map := map[string]string{"myval1": "foo", "myval2": "bar", "yourval1": "baz", "yourval2": "fuz"}
	fmt.Println("MY MAP:", my_map)

	//set all keys into the DB 1

	for k, v := range my_map {
		err = client1.Set(ctx, k, v, 0).Err()
		if err != nil {
			panic(err)
		}
	}

	//scan DB 1 for the keys as it's the most efficient and recommended way
	iter := client1.Scan(ctx, 0, pattern, 0).Iterator()

	for iter.Next(ctx) {
		cur_key := iter.Val()
		fmt.Println("keys", cur_key)

		//get value by the key
		cur_val, err := client1.Get(ctx, cur_key).Result()
		if err != nil {
			panic(err)
		}
		fmt.Println(cur_key, cur_val)

		// copy key/value pairs to the second DB
		err = client2.Set(ctx, cur_key, cur_val, 0).Err()
		if err != nil {
			panic(err)
		}
	}

	if err := iter.Err(); err != nil {
		panic(err)
	}

	fmt.Printf("Successfully copied pattern '%s' keys with values from DB %s to the DB %s \n", args[1], args[2], args[3])
}
