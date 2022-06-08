--CREATE DATABASE IF NOT EXISTS food_at_home;

\c food_at_home

DROP TABLE cookbook; 
DROP TABLE pantry; 

DROP TABLE recipe; 
DROP TABLE ingredient_list; 
DROP TABLE ingredient; 
DROP TABLE measurement; 
DROP TABLE user_account; 

CREATE TABLE IF NOT EXISTS user_account (
    user_id SERIAL UNIQUE PRIMARY KEY, 
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL, 
    user_account_name TEXT UNIQUE NOT NULL, 
    email TEXT UNIQUE NOT NULL, 
    pswrd TEXT NOT NULL
); 

CREATE TABLE IF NOT EXISTS measurement (
    measurement_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    full_name TEXT NOT NULL,
    alt_name_1 TEXT, 
    alt_name_2 TEXT, 
    alt_name_3 TEXT
);

CREATE TABLE IF NOT EXISTS ingredient (
    ingredient_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    edamam_id TEXT NOT NULL, 
    ingredient_name TEXT NOT NULL, 
    link TEXT NOT NULL, 
    calories_k INT, 
    fat_g INT, 
    protein_g INT, 
    carbs_g INT, 
    expiration DATE, 
    fk_measurement INT, 

    CONSTRAINT fk_measurement
        FOREIGN KEY (fk_measurement) 
            REFERENCES measurement(measurement_id)
); 

CREATE TABLE IF NOT EXISTS ingredient_list(
    list_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    ingredient_1_id INT NOT NULL, 
    ingredient_1_quantity FLOAT, 
    ingredient_2_id INT, 
    ingredient_2_quantity FLOAT, 
    ingredient_3_id INT, 
    ingredient_3_quantity FLOAT, 
    ingredient_4_id INT, 
    ingredient_4_quantity FLOAT, 
    ingredient_5_id INT, 
    ingredient_5_quantity FLOAT,
    ingredient_6_id INT, 
    ingredient_6_quantity FLOAT, 
    ingredient_7_id INT, 
    ingredient_7_quantity FLOAT, 
    ingredient_8_id INT, 
    ingredient_8_quantity FLOAT, 
    ingredient_9_id INT, 
    ingredient_9_quantity FLOAT, 
    ingredient_10_id INT, 
    ingredient_10_quantity FLOAT, 
    ingredient_11_id INT, 
    ingredient_11_quantity FLOAT, 
    ingredient_12_id INT, 
    ingredient_12_quantity FLOAT, 
    ingredient_13_id INT, 
    ingredient_13_quantity FLOAT, 
    ingredient_14_id INT, 
    ingredient_14_quantity FLOAT, 
    ingredient_15_id INT, 
    ingredient_15_quantity FLOAT,
    ingredient_16_id INT, 
    ingredient_16_quantity FLOAT, 
    ingredient_17_id INT, 
    ingredient_17_quantity FLOAT, 
    ingredient_18_id INT, 
    ingredient_18_quantity FLOAT, 
    ingredient_19_id INT, 
    ingredient_19_quantity FLOAT, 
    ingredient_20_id INT, 
    ingredient_20_quantity FLOAT, 

    CONSTRAINT ingredient_1_id
        FOREIGN KEY (ingredient_1_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_2_id
        FOREIGN KEY (ingredient_2_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_3_id
        FOREIGN KEY (ingredient_3_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_4_id
        FOREIGN KEY (ingredient_4_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_5_id
        FOREIGN KEY (ingredient_5_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_6_id
        FOREIGN KEY (ingredient_6_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_7_id
        FOREIGN KEY (ingredient_7_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_8_id
        FOREIGN KEY (ingredient_8_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_9_id
        FOREIGN KEY (ingredient_9_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_10_id
        FOREIGN KEY (ingredient_10_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_11_id
        FOREIGN KEY (ingredient_11_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_12_id
        FOREIGN KEY (ingredient_12_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_13_id
        FOREIGN KEY (ingredient_13_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_14_id
        FOREIGN KEY (ingredient_14_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_15_id
        FOREIGN KEY (ingredient_15_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_16_id
        FOREIGN KEY (ingredient_16_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_17_id
        FOREIGN KEY (ingredient_17_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_18_id
        FOREIGN KEY (ingredient_18_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_19_id
        FOREIGN KEY (ingredient_19_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT ingredient_20_id
        FOREIGN KEY (ingredient_20_id)
            REFERENCES ingredient(ingredient_id)

); 

CREATE TABLE IF NOT EXISTS recipe (
    recipe_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 

    fk_ingredient_list_1 INT NOT NULL,
    list_1_label TEXT,  
    fk_ingredient_list_2 INT, 
    list_2_label TEXT,  
    fk_ingredient_list_3 INT, 
    list_3_label TEXT,  
    
    link TEXT NOT NULL, 
    calories_k INT,
    fat_g INT, 
    protein_g INT, 
    carbs_g INT, 
    servings INT, 

    CONSTRAINT fk_user_id
        FOREIGN KEY (fk_user_id)
            REFERENCES user_account(user_id),

    CONSTRAINT fk_ingredient_list_1
        FOREIGN KEY (fk_ingredient_list_1)
            REFERENCES ingredient_list(list_id),

    CONSTRAINT fk_ingredient_list_2
        FOREIGN KEY (fk_ingredient_list_2)
            REFERENCES ingredient_list(list_id),

    CONSTRAINT fk_ingredient_list_3
        FOREIGN KEY (fk_ingredient_list_3)
            REFERENCES ingredient_list(list_id),
);

CREATE TABLE IF NOT EXISTS cookbook( 
    page_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 
    fk_recipe_id INT,
    recipe_name TEXT, 

    CONSTRAINT fk_recipe_id
        FOREIGN KEY(fk_recipe_id)
            REFERENCES recipe(recipe_id), 

    CONSTRAINT fk_user_id
        FOREIGN KEY(fk_user_id)
            REFERENCES user_account(user_id)

); 

CREATE TABLE IF NOT EXISTS pantry( 
    item_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 
    fk_ingredient_id INT, 
    quantity INT,
    fk_measurement_id INT, 
    date_start DATE, 
    date_expiration DATE, 

    CONSTRAINT fk_user_id
        FOREIGN KEY (fk_user_id)
            REFERENCES user_account(user_id), 

    CONSTRAINT fk_ingredient_id
        FOREIGN KEY (fk_ingredient_id)
            REFERENCES ingredient(ingredient_id),

    CONSTRAINT fk_measurement_id
        FOREIGN KEY (fk_measurement_id)
            REFERENCES measurement(measurement_id)

); 