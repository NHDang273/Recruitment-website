import { BadRequestException, Injectable } from '@nestjs/common';
import { CreateUserCvDto } from './dto/create-resume.dto';
import { UpdateResumeDto } from './dto/update-resume.dto';
import { IUser } from 'src/users/users.interface';
import { Resume, ResumeDocument } from './schemas/resume.schema';
import { SoftDeleteModel } from 'soft-delete-plugin-mongoose';
import { InjectModel } from '@nestjs/mongoose';
import aqp from 'api-query-params';
import mongoose from 'mongoose';
import path from 'path';
import fs from 'fs';
import axios from 'axios';
import FormData from 'form-data';
import chokidar from 'chokidar';

@Injectable()
export class ResumesService {
  private resumesFolderPath = path.join(__dirname, '..', '..', 'public', 'images', 'resume');
  private watcher: chokidar.FSWatcher;

  constructor(
    @InjectModel(Resume.name)
    private resumeModel: SoftDeleteModel<ResumeDocument>
  ) {
    // Initialize the file watcher
    this.watcher = chokidar.watch(this.resumesFolderPath, {
      ignored: /^\./,
      persistent: true
    });

    // Set up event listeners for file changes
    this.watcher.on('add', (filePath) => this.onFileChange(filePath));
    this.watcher.on('change', (filePath) => this.onFileChange(filePath));
  }

  // Method that will be triggered on file changes
  private async onFileChange(filePath: string) {
    if (filePath.endsWith('.pdf')) {
      console.log(`File changed: ${filePath}`);
      await this.sendAllPdfsToFastApi();
    }
  }

  async create(createUserCvDto: CreateUserCvDto, user: IUser) {
    const { url, companyId, jobId } = createUserCvDto;
    const { email, _id } = user;

    const newCV = await this.resumeModel.create({
      url, companyId, email, jobId,
      userId: _id,
      status: "PENDING",
      createdBy: { _id, email },
      history: [
        {
          status: "PENDING",
          updatedAt: new Date,
          updatedBy: {
            _id: user._id,
            email: user.email
          }
        }
      ]
    });

    return {
      _id: newCV?._id,
      createdAt: newCV?.createdAt
    };
  }

  async findAll(currentPage: number, limit: number, qs: string) {
    const { filter, sort, population, projection } = aqp(qs);
    delete filter.current;
    delete filter.pageSize;

    let offset = (+currentPage - 1) * (+limit);
    let defaultLimit = +limit ? +limit : 10;

    const totalItems = (await this.resumeModel.find(filter)).length;
    const totalPages = Math.ceil(totalItems / defaultLimit);

    const result = await this.resumeModel.find(filter)
      .skip(offset)
      .limit(defaultLimit)
      .sort(sort as any)
      .populate(population)
      .select(projection as any)
      .exec();

    return {
      meta: {
        current: currentPage,
        pageSize: limit,
        pages: totalPages,
        total: totalItems
      },
      result
    };
  }

  async findOne(id: string) {
    if (!mongoose.Types.ObjectId.isValid(id)) {
      throw new BadRequestException("not found resume");
    }

    return await this.resumeModel.findById(id);
  }

  async findByUsers(user: IUser) {
    return await this.resumeModel.find({
      userId: user._id,
    })
      .sort("-createdAt")
      .populate([
        {
          path: "companyId",
          select: { name: 1 }
        },
        {
          path: "jobId",
          select: { name: 1 }
        }
      ]);
  }

  async update(_id: string, status: string, user: IUser) {
    if (!mongoose.Types.ObjectId.isValid(_id)) {
      throw new BadRequestException("not found resume");
    }

    const updated = await this.resumeModel.updateOne(
      { _id },
      {
        status,
        updatedBy: {
          _id: user._id,
          email: user.email
        },
        $push: {
          history: {
            status: status,
            updatedAt: new Date(),
            updatedBy: {
              _id: user._id,
              email: user.email
            }
          }
        }
      });

    return updated;
  }

  async remove(id: string, user: IUser) {
    await this.resumeModel.updateOne(
      { _id: id },
      {
        deletedBy: {
          _id: user._id,
          email: user.email
        }
      });
    return this.resumeModel.softDelete({
      _id: id
    });
  }

  /**
   * Gửi tất cả file PDF từ folder resumesFolderPath đến FastAPI
   */
  async sendAllPdfsToFastApi(): Promise<void> {
    if (!fs.existsSync(this.resumesFolderPath)) {
      fs.mkdirSync(this.resumesFolderPath, { recursive: true });
    }

    const files = fs.readdirSync(this.resumesFolderPath).filter((file) => file.endsWith('.pdf'));

    for (const file of files) {
      const filePath = path.join(this.resumesFolderPath, file);

      const formData = new FormData();
      formData.append('file', fs.createReadStream(filePath));

      try {
        const response = await axios.post('http://localhost:8000/api/upload_pdf', formData, {
          headers: {
            ...formData.getHeaders(),
          },
        });
        console.log(`Uploaded ${file} successfully:`, response.data);
      } catch (error) {
        console.error(`Failed to upload ${file}:`, error.message);
      }
    }
  }
}
