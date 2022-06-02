--CREATE DATABASE IF NOT EXISTS food_at_home;

\c food_at_home

DROP TABLE fact_cookbook; 
DROP TABLE fact_pantry; 

DROP TABLE dim_recipe; 
DROP TABLE dim_ingredient; 
DROP TABLE dim_measurement; 
DROP TABLE dim_user; 

CREATE TABLE IF NOT EXISTS dim_user (
    user_id SERIAL UNIQUE PRIMARY KEY, 
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL, 
    user_name TEXT UNIQUE NOT NULL, 
    email TEXT UNIQUE NOT NULL, 
    pswrd TEXT NOT NULL
); 

CREATE TABLE IF NOT EXISTS dim_measurement (
    measurement_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    measurement_name TEXT NOT NULL,
    quantity_metric TEXT, 
    quantity_imperial TEXT
);

CREATE TABLE IF NOT EXISTS dim_ingredient (
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
            REFERENCES dim_measurement(measurement_id)
);

CREATE TABLE IF NOT EXISTS dim_recipe (
    recipe_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 
    link TEXT NOT NULL, 
    calories_k INT,
    fat_g INT, 
    protein_g INT, 
    carbs_g INT, 
    servings INT, 
    ingredient_1_id INT, 
    ingredient_2_id INT, 
    ingredient_3_id INT, 
    ingredient_4_id INT, 
    ingredient_5_id INT, 
    ingredient_6_id INT, 
    ingredient_7_id INT, 
    ingredient_8_id INT, 
    ingredient_9_id INT, 
    ingredient_10_id INT, 
    ingredient_11_id INT, 

    CONSTRAINT ingredient_1_id
        FOREIGN KEY (ingredient_1_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_1_quantity FLOAT, 

    CONSTRAINT ingredient_2_id
        FOREIGN KEY (ingredient_2_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_2_quantity FLOAT, 

    CONSTRAINT ingredient_3_id
        FOREIGN KEY (ingredient_3_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_3_quantity FLOAT, 

    CONSTRAINT ingredient_4_id
        FOREIGN KEY (ingredient_4_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_4_quantity FLOAT, 

    CONSTRAINT ingredient_5_id
        FOREIGN KEY (ingredient_5_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_5_quantity FLOAT,

    CONSTRAINT ingredient_6_id
        FOREIGN KEY (ingredient_6_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_6_quantity FLOAT, 

    CONSTRAINT ingredient_7_id
        FOREIGN KEY (ingredient_7_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_7_quantity FLOAT, 

    CONSTRAINT ingredient_8_id
        FOREIGN KEY (ingredient_8_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_8_quantity FLOAT, 

    CONSTRAINT ingredient_9_id
        FOREIGN KEY (ingredient_9_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_9_quantity FLOAT, 

    CONSTRAINT ingredient_10_id
        FOREIGN KEY (ingredient_10_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_10_quantity FLOAT, 

    CONSTRAINT ingredient_11_id
        FOREIGN KEY (ingredient_11_id)
            REFERENCES dim_ingredient(ingredient_id),
    ingredient_11_quantity FLOAT, 
        
    CONSTRAINT fk_user_id 
        FOREIGN KEY (fk_user_id)
            REFERENCES dim_user(user_id)
); 

CREATE TABLE IF NOT EXISTS fact_cookbook( 
    page_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 
    fk_recipe_id INT,
    recipe_name TEXT, 

    CONSTRAINT fk_recipe_id
        FOREIGN KEY(fk_recipe_id)
            REFERENCES dim_recipe(recipe_id), 

    CONSTRAINT fk_user_id
        FOREIGN KEY(fk_user_id)
            REFERENCES dim_user(user_id)

); 

CREATE TABLE IF NOT EXISTS fact_pantry( 
    item_id INT UNIQUE GENERATED ALWAYS AS IDENTITY, 
    fk_user_id INT, 
    fk_ingredient_id INT, 
    quantity INT,
    fk_measurement_id INT, 
    date_start DATE, 
    date_expiration DATE, 

    CONSTRAINT fk_user_id
        FOREIGN KEY (fk_user_id)
            REFERENCES dim_user(user_id), 

    CONSTRAINT fk_ingredient_id
        FOREIGN KEY (fk_ingredient_id)
            REFERENCES dim_ingredient(ingredient_id),

    CONSTRAINT fk_measurement_id
        FOREIGN KEY (fk_measurement_id)
            REFERENCES dim_measurement(measurement_id)

); 