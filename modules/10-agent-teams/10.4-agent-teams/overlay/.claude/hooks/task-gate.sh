#!/bin/bash
node --test >/dev/null 2>&1 && exit 0
echo "Тести червоні. Задача не закривається, поки node --test не позеленіє." >&2
exit 2
