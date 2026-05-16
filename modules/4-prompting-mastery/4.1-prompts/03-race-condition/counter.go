package main

import (
	"fmt"
	"sync"
)

type Counter struct {
	value int
}

func (c *Counter) Increment() {
	c.value = c.value + 1
}

func (c *Counter) Value() int {
	return c.value
}

func main() {
	c := &Counter{}
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Increment()
		}()
	}

	wg.Wait()
	fmt.Println("expected: 1000, got:", c.Value())
}
