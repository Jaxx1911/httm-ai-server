-- Xóa các bảng nếu tồn tại theo thứ tự phụ thuộc để tránh lỗi
DROP TABLE IF EXISTS "ModelDataset" CASCADE;
DROP TABLE IF EXISTS "Sample" CASCADE;
DROP TABLE IF EXISTS "Model" CASCADE;
DROP TABLE IF EXISTS "Dataset" CASCADE;
DROP TABLE IF EXISTS "Admin" CASCADE;

-- 1. Bảng "Admin"
-- (Đã sửa "emai" -> "email")
CREATE TABLE "Admin" (
    "admin_id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL, -- << SỬA LỖI GÕ PHÍM
    "phone" VARCHAR(255) NOT NULL
);

-- 2. Bảng "Dataset"
-- (Đã thêm "Adminadmin_id" làm khóa ngoại)
CREATE TABLE "Dataset" (
    "dataset_ID" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "status" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "Adminadmin_id" VARCHAR(255) NOT NULL -- << THÊM MỚI
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
    "Adminadmin_id" VARCHAR(255) NOT NULL -- Khóa ngoại
);

-- 4. Bảng "Sample" (Phụ thuộc vào "Dataset")
-- (Đã xóa "Adminadmin_id")
-- (Bạn cần DROP bảng "Sample" cũ trước nếu đã tạo)

-- Tạo lại bảng "Sample" với cột "source"
CREATE TABLE "Sample" (
    "sample_id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "input_text" TEXT NOT NULL,
    "target_summary" TEXT NOT NULL,
    "category" VARCHAR(255) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "language" VARCHAR(255) NOT NULL, -- Sẽ được gán 'vi' khi import
    "created_at" DATE NOT NULL,      -- Sẽ được gán CURRENT_DATE khi import
    "source" VARCHAR(255) NULL,      -- << THÊM CỘT MỚI (để là NULL nếu một số file không có)
    "Datasetdataset_ID" VARCHAR(255) NOT NULL
    
);

-- 5. Bảng "ModelDataset" (Bảng nối Many-to-Many)
-- (Đã xóa "modeldataset_id" và thêm Khóa chính tổ hợp)
CREATE TABLE "ModelDataset" (
    "weight" REAL NOT NULL,
    "notes" VARCHAR(255) NOT NULL,
    "Datasetdataset_ID" VARCHAR(255) NOT NULL, -- Khóa ngoại
    "Modelmodel_id" VARCHAR(255) NOT NULL, -- Khóa ngoại
    
    -- << THÊM KHÓA CHÍNH TỔ HỢP
    PRIMARY KEY ("Datasetdataset_ID", "Modelmodel_id")
);

-- --- THÊM CÁC RÀNG BUỘC KHÓA NGOẠI (FOREIGN KEY) ---

-- Ràng buộc từ "Dataset" -> "Admin" (MỚI)
ALTER TABLE "Dataset"
ADD CONSTRAINT "FK_Dataset_Admin"
FOREIGN KEY ("Adminadmin_id") REFERENCES "Admin" ("admin_id");

-- Ràng buộc từ "Model" -> "Admin"
ALTER TABLE "Model"
ADD CONSTRAINT "FK_Model_Admin"
FOREIGN KEY ("Adminadmin_id") REFERENCES "Admin" ("admin_id");

-- Ràng buộc từ "Sample" -> "Dataset"
ALTER TABLE "Sample"
ADD CONSTRAINT "FK_Sample_Dataset"
FOREIGN KEY ("Datasetdataset_ID") REFERENCES "Dataset" ("dataset_ID");

-- Ràng buộc từ "ModelDataset" -> "Dataset"
ALTER TABLE "ModelDataset"
ADD CONSTRAINT "FK_ModelDataset_Dataset"
FOREIGN KEY ("Datasetdataset_ID") REFERENCES "Dataset" ("dataset_ID");

-- Ràng buộc từ "ModelDataset" -> "Model"
ALTER TABLE "ModelDataset"
ADD CONSTRAINT "FK_ModelDataset_Model"
FOREIGN KEY ("Modelmodel_id") REFERENCES "Model" ("model_id");

-- Ràng buộc FK_Sample_Admin đã được tự động loại bỏ
-- khi xóa cột "Adminadmin_id" khỏi bảng "Sample".