У `report.js` функція `buildReport(orders)` робить окремий запит до БД на КОЖНЕ
замовлення (`db.findUser`) — це N+1.

Завдання: усунь N+1. Заверши задачу одним батч-запитом `db.findUsersByIds(ids)` замість
N окремих викликів `db.findUser`. Результат `buildReport` має лишитися тим самим
(той самий список `{ order, user }`).

Змінюй лише `report.js`. Не чіпай `db.js`.
