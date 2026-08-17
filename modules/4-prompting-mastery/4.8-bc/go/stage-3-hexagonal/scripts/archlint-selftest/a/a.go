package a

// НАВМИСНЕ порушення: конфіг поруч забороняє a залежати від b.
// Якщо go-arch-lint цього не бачить — він зламаний.
import "archlint-selftest/b"

func Hello() string {
	return b.Name()
}
