DROP TABLE IF EXISTS "ModelDataset" CASCADE;
DROP TABLE IF EXISTS "Sample" CASCADE;
DROP TABLE IF EXISTS "Model" CASCADE;
DROP TABLE IF EXISTS "Dataset" CASCADE;
DROP TABLE IF EXISTS "Admin" CASCADE;

-- 1. Bảng "Admin"
CREATE TABLE "Admin" (
    "admin_id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL, 
    "phone" VARCHAR(255) NOT NULL
);

-- 2. Bảng "Dataset"
CREATE TABLE "Dataset" (
    "dataset_ID" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "status" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "Adminadmin_id" VARCHAR(255) NOT NULL 
);

-- 3. Bảng "Model" (Phụ thuộc vào "Admin")
CREATE TABLE "Model" (
    "model_id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "accuracy" REAL NOT NULL,
    "precision" DOUBLE PRECISION NOT NULL,
    "recall" DOUBLE PRECISION NOT NULL,
    "F1Score" DOUBLE PRECISION NOT NULL,
    "path" VARCHAR(255) NOT NULL,
    "status" VARCHAR(255) NOT NULL,
    "finetune_time" TIME NOT NULL,
    "parameter" DOUBLE PRECISION NOT NULL,
    "baseModel" VARCHAR(255) NOT NULL,
    "Adminadmin_id" VARCHAR(255) NOT NULL 
);

-- 4. Bảng "Sample"

CREATE TABLE "Sample" (
    "sample_id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "input_text" TEXT NOT NULL,
    "target_summary" TEXT NOT NULL,
    "category" VARCHAR(255) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "language" VARCHAR(255) NOT NULL, -- Sẽ được gán 'vi' khi import
    "created_at" DATE NOT NULL,      -- Sẽ được gán CURRENT_DATE khi import
    "source" VARCHAR(255) NULL,     
    "Datasetdataset_ID" VARCHAR(255) NOT NULL
    
);

-- 5. Bảng "ModelDataset" 
CREATE TABLE "ModelDataset" (
    "weight" REAL NOT NULL,
    "notes" VARCHAR(255) NOT NULL,
    "Datasetdataset_ID" VARCHAR(255) NOT NULL, -- Khóa ngoại
    "Modelmodel_id" VARCHAR(255) NOT NULL, -- Khóa ngoại
    PRIMARY KEY ("Datasetdataset_ID", "Modelmodel_id")
);

-- --- THÊM CÁC RÀNG BUỘC KHÓA NGOẠI (FOREIGN KEY) ---

ALTER TABLE "Dataset"
ADD CONSTRAINT "FK_Dataset_Admin"
FOREIGN KEY ("Adminadmin_id") REFERENCES "Admin" ("admin_id");

ALTER TABLE "Model"
ADD CONSTRAINT "FK_Model_Admin"
FOREIGN KEY ("Adminadmin_id") REFERENCES "Admin" ("admin_id");

ALTER TABLE "Sample"
ADD CONSTRAINT "FK_Sample_Dataset"
FOREIGN KEY ("Datasetdataset_ID") REFERENCES "Dataset" ("dataset_ID");

ALTER TABLE "ModelDataset"
ADD CONSTRAINT "FK_ModelDataset_Dataset"
FOREIGN KEY ("Datasetdataset_ID") REFERENCES "Dataset" ("dataset_ID");

ALTER TABLE "ModelDataset"
ADD CONSTRAINT "FK_ModelDataset_Model"
FOREIGN KEY ("Modelmodel_id") REFERENCES "Model" ("model_id");
