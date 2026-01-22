import java.util.ArrayList;
import java.util.List;

class BuilderExample {
    public static class Person {
        private final String name;
        private final int age;
        private final String address;
        private final List<Person> friends;

        private Person(Builder builder) {
            this.name = builder.name;
            this.age = builder.age;
            this.address = builder.address;
            this.friends = builder.friends;
        }

        public List<Person> getFriends() {
            return friends;
        }

        public String getName() {
            return name;
        }

        public int getAge() {
            return age;
        }

        public String getAddress() {
            return address;
        }

        public static class Builder {
            private String name;
            private int age;
            private String address;
            private final List<Person> friends = new ArrayList<>();

            public Builder setName(String name) {
                this.name = name;
                return this;
            }

            public Builder setAge(int age) {
                this.age = age;
                return this;
            }

            public Builder setAddress(String address) {
                this.address = address;
                return this;
            }

            public Builder addFriend(Person friend) {
                this.friends.add(friend);
                return this;
            }

            public Person build() {
                return new Person(this);
            }
        }

        @Override
        public String toString() {
            return "Person{name='" + name + "', age=" + age + ", address='" + address + "'}";
        }
    }

    public static void main(String[] args) {
        Person John = new Person.Builder()
                .setName("John Doe")
                .setAge(30)
                .setAddress("123 Main St")
                .build();
        Person Jane = new Person.Builder()
                .setName("Jane Doe")
                .setAge(25)
                .setAddress("456 Main St")
                .addFriend(John).build();

        System.out.println(John);
        System.out.println(Jane);
        System.out.println(Jane.getFriends());
    }
}
