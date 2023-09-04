from pydantic import BaseModel, ValidationError
import requests
import unittest
import json
from config import API_KEY  # Импорт API_KEY из файла config.py


# Определение ожидаемой модели ответа для валидации
class PetResponse(BaseModel):
    age: int
    animal_type: str
    created_at: float
    id: str
    name: str
    pet_photo: str
    user_id: str


# Набор тестов для API создания питомца
class TestCreatePetSimple(unittest.TestCase):

    # Инициализация перед каждым тестовым случаем
    def setUp(self):
        self.base_url = "http://petfriends.skillfactory.ru/api"
        self.auth_key = API_KEY  # Использование API_KEY из config.py

    # Проверка наличия всех необходимых полей в запросе
    def assert_payload(self, payload):
        assert 'name' in payload, "Запрос должен содержать 'name'"
        assert 'animal_type' in payload, "Запрос должен содержать 'animal_type'"
        assert 'age' in payload, "Запрос должен содержать 'age'"

    # Проверка схемы ответа на соответствие ожидаемой модели
    def assert_response_schema(self, response_text):
        try:
            PetResponse(**json.loads(response_text))
        except ValidationError as e:
            self.fail(f"Не удалось провалидировать схему ответа: {e}")

    # Создание питомца и проверка корректности ответа
    def create_and_assert_pet(self, name, animal_type, age):
        headers = {'Authorization': f"Bearer {self.auth_key}"}
        payload = {'name': name, 'animal_type': animal_type, 'age': age}

        # Проверка корректности payload
        self.assert_payload(payload)

        response = requests.post(f"{self.base_url}/create_pet_simple", headers=headers, data=payload)

        # Вывод полного ответа для анализа
        print(f"Полученный ответ: {response.json()}")

        self.assertEqual(response.status_code, 200)
        self.assert_response_schema(response.text)

        response_data = PetResponse(**json.loads(response.text))
        self.assertEqual(response_data.name, name)
        self.assertEqual(response_data.animal_type, animal_type)
        self.assertEqual(response_data.age, age)

    # Проваленный тест создания питомца
    def create_and_assert_pet_failure(self, name, animal_type, age, expected_status, auth_key=None):
        headers = {'Authorization': f"Bearer {auth_key if auth_key else self.auth_key}"}
        payload = {'name': name, 'animal_type': animal_type, 'age': age}

        if name and animal_type and age is not None:
            self.assert_payload(payload)

        response = requests.post(f"{self.base_url}/create_pet_simple", headers=headers, data=payload)

        # Вывод полного ответа для анализа
        print(f"Полученный ответ: {response.json() if response.status_code != 403 else response.text}")

        self.assertEqual(response.status_code, expected_status)

        if response.status_code == 200:
            self.assert_response_schema(response.text)

    # Тест создания кошки
    def test_create_pet_with_type_cat(self):
        self.create_and_assert_pet('Мурзик', 'Кошка', 3)

    # Тест создания попугая
    def test_create_pet_with_type_parrot(self):
        self.create_and_assert_pet('Кеша', 'Попугай', 1)

    # Тест создания собаки
    def test_create_pet_simple(self):
        self.create_and_assert_pet('Боб', 'Немецкая овчарка', 2)

    # Тест создания кошки с минимальным возрастом
    def test_create_pet_with_min_age(self):
        self.create_and_assert_pet('Алиса', 'Сиамская кошка', 0)

    # Тест создания собаки с максимальным возрастом
    def test_create_pet_with_max_age(self):
        self.create_and_assert_pet('Чарли', 'Боксер', 25)

    # Тест создания питомца без имени
    def test_create_pet_without_name(self):
        self.create_and_assert_pet_failure(None, 'Немецкая овчарка', 2, 400)

    # Тест создания питомца без типа
    def test_create_pet_without_type(self):
        self.create_and_assert_pet_failure('Боб', None, 2, 400)

    # Тест создания питомца с недействительным ключом авторизации
    def test_create_pet_with_invalid_auth_key(self):
        self.create_and_assert_pet_failure('Боб', 'Немецкая овчарка', 2, 403, auth_key='invalid')

    # Тест создания питомца с отрицательным возрастом
    def test_create_pet_with_negative_age(self):
        self.create_and_assert_pet_failure('Боб', 'Собака', -1, 400)

    # Тест создания питомца с нереальным возрастом
    def test_create_pet_with_excessive_age(self):
        self.create_and_assert_pet_failure('Боб', 'Собака', 100, 400)


if __name__ == "__main__":
    unittest.main()
