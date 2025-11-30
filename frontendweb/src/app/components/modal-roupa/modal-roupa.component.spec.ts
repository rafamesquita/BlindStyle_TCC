import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModalRoupaComponent } from './modal-roupa.component';

describe('ModalRoupaComponent', () => {
  let component: ModalRoupaComponent;
  let fixture: ComponentFixture<ModalRoupaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModalRoupaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModalRoupaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
